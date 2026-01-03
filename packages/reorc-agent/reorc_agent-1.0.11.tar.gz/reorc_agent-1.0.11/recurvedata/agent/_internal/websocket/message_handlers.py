import asyncio
import time
from abc import ABC, abstractmethod

import httpx
from loguru import logger

from recurvedata.agent._internal import host, worker
from recurvedata.agent._internal.cube.query_service import cube_query_service
from recurvedata.agent._internal.schemas import (
    CancelPayload,
    CubeSqlRequestPayload,
    CubeSqlResponsePayload,
    Heartbeat,
    HttpRequestPayload,
    HttpResponsePayload,
    SourceCodeExecPayload,
    TaskStatus,
    WorkerManagementPayload,
)
from recurvedata.agent._internal.task_executor import TaskExecutor
from recurvedata.agent._internal.task_logger import TaskLogCollector, TaskLogger
from recurvedata.agent._internal.task_manager import global_task_manager
from recurvedata.agent._internal.websocket.connector import WebSocketConnector
from recurvedata.agent._internal.websocket.schemas import MessageType, WebSocketMessage
from recurvedata.agent.dpserver.client import request_dpserver
from recurvedata.agent.dpserver.schema import DPServerRequestPayload

from ..worker_management import WorkerManagementTask


class BaseMessageHandler(ABC):
    _bind_message_type = None

    @abstractmethod
    async def handle(self, message: WebSocketMessage, ws_connector: WebSocketConnector):
        raise NotImplementedError


class MessageHandlerRegistry:
    def __init__(self):
        self.handlers = {}

    def register(self, message_type: MessageType, handler: BaseMessageHandler):
        self.handlers[message_type] = handler

    def register_handler(self):
        """
        Decorator: Automatically register handler to registry

        Args:
            message_type: Message type used as registry key
        """

        def decorator(handler_class):
            # Ensure handler_class is a subclass of BaseMessageHandler
            if not issubclass(handler_class, BaseMessageHandler):
                raise ValueError(f"Handler class {handler_class.__name__} must inherit from BaseMessageHandler")

            message_type = handler_class._bind_message_type
            # check in development stage
            assert message_type in MessageType, f"Register Message Handler Error, unknown message type: {message_type}"

            # Register to registry
            self.register(message_type, handler_class())

            return handler_class

        return decorator

    def get_handler(self, message_type: MessageType | None) -> BaseMessageHandler | None:
        """Get handler for specified message type"""
        return self.handlers.get(message_type)

    def get_all_handlers(self) -> dict:
        """Get all registered handlers"""
        return self.handlers.copy()

    def has_handler(self, message_type: str | None) -> bool:
        """Check if handler is registered for specified message type"""
        return message_type in self.handlers


# global registry instance
registry = MessageHandlerRegistry()


@registry.register_handler()
class HeartBeatRequestMessageHandler(BaseMessageHandler):
    """
    Handle heartbeat request message from server.
    Reply with heartbeat message to server.
    """

    _bind_message_type = MessageType.HEARTBEAT_REQUEST

    async def handle(self, message: WebSocketMessage, ws_connector: WebSocketConnector):
        logger.info(f"received heartbeat request: {message}")
        path = worker.get_docker_root_dir()
        payload = Heartbeat(
            agent_id=ws_connector.config.agent_id,
            metrics=host.get_host_metrics(path=path),
            service_status=worker.get_service_status(),
        )
        message = WebSocketMessage(
            type=MessageType.HEARTBEAT,
            payload=payload.model_dump(mode="json"),
            reply_to=message.message_id,  # reply to the same message id
        )
        await ws_connector.send_json(message.model_dump(mode="json"))


@registry.register_handler()
class WorkerManagementMessageHandler(BaseMessageHandler):
    _bind_message_type = MessageType.WORKER_MANAGEMENT

    async def handle(self, message: WebSocketMessage, ws_connector: WebSocketConnector):
        logger.info(f"received worker management message: {message.type}-{message.message_id}")

        # Setup real-time log collection
        log_collector = TaskLogCollector(ws_connector=ws_connector, message_id=message.message_id)
        await log_collector.start()
        task_logger = TaskLogger(log_collector)

        try:
            await task_logger.info(f"Processing worker management task: {message.message_id}")

            payload = WorkerManagementPayload.model_validate(
                {
                    "action": message.payload.get("action"),
                    # inner payload is task payload
                    "payload": message.payload,
                }
            )

            await task_logger.info(f"Worker management action: {payload.action}")
            result = await WorkerManagementTask.handle(payload, task_logger)

            await task_logger.info("Worker management task completed successfully")

            # flush logs before change task to SUCCESS status
            await log_collector.stop()

            response_message = WebSocketMessage(
                type=MessageType.RESULT,
                payload={
                    "result": result.model_dump(mode="json") if result else None,
                    "error": None,
                    "status": TaskStatus.SUCCESS,
                },
                reply_to=message.message_id,
                message_id=message.message_id,
            )
            await ws_connector.send_json(response_message.model_dump(mode="json"))
            return result

        except Exception as e:
            await task_logger.error(f"Worker management task failed: {e}")
            raise
        finally:
            await log_collector.stop()


@registry.register_handler()
class CancelMessageHandler(BaseMessageHandler):
    _bind_message_type = MessageType.CANCEL

    async def handle(self, message: WebSocketMessage, ws_connector: WebSocketConnector):
        logger.info(f"received cancel message: {message.type}-{message.message_id}")
        task_id = CancelPayload.model_validate(message.payload).task_id
        await global_task_manager.cancel_task(task_id)


@registry.register_handler()
class BusinessMessageHandler(BaseMessageHandler):
    """
    Handle business message from server.
    Forward dpserver requests to dpserver and return the response.
    """

    _bind_message_type = MessageType.BUSINESS

    async def handle(self, message: WebSocketMessage, ws_connector: WebSocketConnector):

        logger.info(f"received business message: {message.type}-{message.message_id}")

        # Setup real-time log collection
        log_collector = TaskLogCollector(ws_connector=ws_connector, message_id=message.message_id)
        await log_collector.start()
        task_logger = TaskLogger(log_collector)

        try:
            await task_logger.info(f"Processing business request: {message.message_id}")

            # Parse request payload
            payload = DPServerRequestPayload.model_validate(message.payload)
            await task_logger.info(f"Business request type: {type(payload).__name__}")

            result = None
            # Call dpserver to process request
            result = await request_dpserver(payload)
            await task_logger.info("DPServer request processed successfully")

            # flush logs before change task to SUCCESS status
            await log_collector.stop()

            # Send success response, DPServer has nothing need to be sent as log
            response_message = WebSocketMessage(
                type=MessageType.RESULT,
                payload={
                    "result": result.model_dump() if result else None,
                    "error": result.error if result else None,
                    "status": TaskStatus.SUCCESS if result.ok else TaskStatus.FAILED,
                },
                reply_to=message.message_id,
                message_id=message.message_id,
            )
            await ws_connector.send_json(response_message.model_dump(mode="json"))
            # return for logger
            return result

        except Exception as e:
            await task_logger.error(f"Business request {message.message_id} failed: {e}")
            await task_logger.error(f"Business request {message.message_id} payload: {payload}")
            await task_logger.error(f"Business request {message.message_id} result: {result}")
            raise
        finally:
            await log_collector.stop()


@registry.register_handler()
class SourceCodeExecMessageHandler(BaseMessageHandler):
    _bind_message_type = MessageType.SOURCE_CODE_EXEC

    async def handle(self, message: WebSocketMessage, ws_connector: WebSocketConnector):
        logger.info(f"received source code exec message: {message.type}-{message.message_id}")
        payload = SourceCodeExecPayload.model_validate(message.payload)

        # Create TaskExecutor with WebSocket connector for real-time log reporting
        task_executor = TaskExecutor(ws_connector=ws_connector, message_id=message.message_id)
        result = await task_executor.execute(payload)

        response_message = WebSocketMessage(
            type=MessageType.RESULT,
            payload=result.model_dump(),
            reply_to=message.message_id,
            message_id=message.message_id,
        )
        await ws_connector.send_json(response_message.model_dump(mode="json"))

        return result


@registry.register_handler()
class HttpMessageHandler(BaseMessageHandler):
    """
    HTTP over Websocket
    Agent proxy the http request.
    """

    _bind_message_type = MessageType.HTTP_REQUEST

    async def handle(self, message: WebSocketMessage, ws_connector: WebSocketConnector):

        logger.info(f"received http request message: {message.type}-{message.message_id}")

        # Setup real-time log collection
        log_collector = TaskLogCollector(ws_connector=ws_connector, message_id=message.message_id)
        await log_collector.start()
        task_logger = TaskLogger(log_collector)

        try:
            await task_logger.info(f"Processing HTTP request: {message.message_id}")

            # Parse and validate payload
            payload = HttpRequestPayload.model_validate(message.payload)
            await task_logger.info(f"HTTP {payload.method} request to {payload.url}")

            timeout = httpx.Timeout(message.max_duration)
            # Make HTTP request
            async with httpx.AsyncClient(timeout=timeout) as client:
                try:
                    response = await client.request(
                        method=payload.method,
                        url=payload.url,
                        params=payload.params,
                        headers=payload.headers,
                        json=payload.body,
                    )
                    await task_logger.info(f"HTTP request successful with code: {response.status_code}")
                except httpx.RequestError as e:
                    await task_logger.error(f"HTTP request failed: {e}")
                    response_payload = HttpResponsePayload(
                        status_code=500,
                        headers={},
                        data=str(e),
                        url=payload.url,
                    )
                else:
                    # Prepare response payload with complete information
                    response_payload = HttpResponsePayload(
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        data=response.text,
                        url=str(response.url),
                    )

            await task_logger.info("HTTP request processing completed")

            # flush logs before send response
            await log_collector.stop()

            # Send response
            response_message = WebSocketMessage(
                type=MessageType.HTTP_RESPONSE,
                payload=response_payload.model_dump(),
                reply_to=message.message_id,
                message_id=message.message_id,
            )
            await ws_connector.send_json(response_message.model_dump(mode="json"))
            return response_payload

        except Exception as e:
            await task_logger.error(f"HTTP request {message.message_id} processing failed: {e}")
            await task_logger.error(f"HTTP request {message.message_id} payload: {payload}")
            raise
        finally:
            await log_collector.stop()


@registry.register_handler()
class CubeSqlMessageHandler(BaseMessageHandler):
    """
    SQL over Websocket
    Agent executes SQL queries and returns results.
    """

    _bind_message_type = MessageType.CUBE_SQL_REQUEST

    async def handle(self, message: WebSocketMessage, ws_connector: WebSocketConnector):

        logger.info(f"received sql request message: {message.type}-{message.message_id}")

        # Setup real-time log collection
        log_collector = TaskLogCollector(ws_connector=ws_connector, message_id=message.message_id)
        await log_collector.start()
        task_logger = TaskLogger(log_collector)

        try:
            await task_logger.info(f"Processing SQL query: {message.message_id}")

            payload = CubeSqlRequestPayload.model_validate(message.payload)
            await task_logger.info(f"SQL query to database: {payload.database}")

            start_time = time.time()
            SEMANTIC_QUERY_TIMEOUT = 59
            result_data = None
            success = True
            error_message = None
            query_timeout = min(message.max_duration, SEMANTIC_QUERY_TIMEOUT)

            try:
                # Execute SQL query using CubeQueryService with timeout from WebSocket message
                await task_logger.info(f"Executing SQL query with timeout={query_timeout}s")
                result_data = await cube_query_service.execute_sql_query(payload, timeout=query_timeout)
                await task_logger.info("SQL query executed successfully")
            except asyncio.TimeoutError as e:
                await task_logger.error(f"SQL query timed out: {str(e)}")
                success = False
                error_message = str(e)
                result_data = None
            except Exception as e:
                await task_logger.error(f"SQL query execution failed: {str(e)}")
                success = False
                error_message = str(e)
                result_data = None
            finally:
                execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                if result_data is not None:
                    returned_msg = f"{len(result_data)} rows" if isinstance(result_data, list) else str(result_data)
                else:
                    returned_msg = "no data (error occurred)"
                await task_logger.info(f"SQL query executed in {execution_time:.2f}ms, returned {returned_msg}")

            response_payload = CubeSqlResponsePayload(
                success=success, data=result_data, error=error_message, execution_time_ms=execution_time
            )

            # flush logs before send response
            await log_collector.stop()

            response_message = WebSocketMessage(
                type=MessageType.CUBE_SQL_RESPONSE,
                payload=response_payload.model_dump(),
                reply_to=message.message_id,
                message_id=message.message_id,
            )
            await ws_connector.send_json(response_message.model_dump())
            return response_payload

        except Exception as e:
            await task_logger.error(f"SQL query {message.message_id} processing failed: {e}")
            await task_logger.error(f"SQL query {message.message_id} payload: {payload}")
            raise
        finally:
            await log_collector.stop()
