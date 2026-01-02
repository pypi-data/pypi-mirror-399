"""
Task Log Real-time Collection and Reporting Module

Why this module exists:
- loguru only outputs logs to console/file locally
- We need to send task execution logs to server in real-time via WebSocket
- Server needs to monitor task progress and collect logs for debugging

When to use this instead of loguru:
- Use this module when you need real-time log reporting to server
- Use loguru for local logging (debug, info, error messages)
- This module automatically outputs to console AND sends to server

Usage:
- All message handlers use this for task execution logging
- Logs are sent every `_report_interval` seconds to server via RESULT message type
- Console output remains the same as before
"""

import asyncio
from datetime import datetime, timezone
from typing import Any

from loguru import logger

from .schemas import TaskStatus
from .websocket.schemas import MessageType, WebSocketMessage


class TaskLogCollector:
    """
    Task log collector that captures logs during task execution and sends them
    to the server via WebSocket in real-time.
    """

    def __init__(self, ws_connector: Any, message_id: str | None = None):
        self.ws_connector = ws_connector
        self.message_id = message_id
        self.log_queue = asyncio.Queue()
        self._report_task: asyncio.Task | None = None
        self._report_interval = 0.5  # Report logs every 500ms
        self._is_running = False

    async def start(self) -> None:
        """Start the log collector and reporting task."""
        if self._is_running:
            return

        self._is_running = True
        self._report_task = asyncio.create_task(self._report_logs_loop())

    async def stop(self) -> None:
        """Stop the log collector and send any remaining logs."""
        if not self._is_running:
            return

        self._is_running = False

        # Send any remaining logs
        await self._flush_logs()

        # Cancel the reporting task
        if self._report_task:
            self._report_task.cancel()
            try:
                await self._report_task
            except asyncio.CancelledError:
                pass

    async def add_log(self, message: str, level: str = "info") -> None:
        """Add a log message to the collector."""
        formatted_message = self._format_log_message(message, level)

        # Add to queue for real-time reporting
        await self.log_queue.put(formatted_message)

    async def _report_logs_loop(self) -> None:
        """Background task to report logs to server periodically."""
        while self._is_running:
            try:
                # Collect logs from queue
                logs_to_send = []
                while not self.log_queue.empty():
                    try:
                        log_message = self.log_queue.get_nowait()
                        logs_to_send.append(log_message)
                    except asyncio.QueueEmpty:
                        break

                # Send logs if any
                if logs_to_send:
                    await self._send_logs_to_server(logs_to_send)

                # Wait for next interval
                await asyncio.sleep(self._report_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in log reporting loop: {e}")
                await asyncio.sleep(self._report_interval)

    async def _send_logs_to_server(self, logs: list[str]) -> None:
        """Send logs to server via WebSocket."""
        try:
            message = WebSocketMessage(
                type=MessageType.RESULT,
                payload={
                    "status": TaskStatus.RUNNING,
                    "logs": logs,
                },
                reply_to=self.message_id,
                message_id=self.message_id,
            )

            await self.ws_connector.send_json(message.model_dump(mode="json"))

        except Exception as e:
            logger.error(f"Failed to send logs to server: {e}")

    async def _flush_logs(self) -> None:
        """Flush any remaining logs in the queue."""
        remaining_logs = []
        while not self.log_queue.empty():
            try:
                log_message = self.log_queue.get_nowait()
                remaining_logs.append(log_message)
            except asyncio.QueueEmpty:
                break

        if remaining_logs:
            await self._send_logs_to_server(remaining_logs)

    def _format_log_message(self, message: str, level: str = "info") -> str:
        """Format log message with timestamp and level, matching loguru's default format."""

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        return f"{timestamp} | {level.upper()} | {message}"


class TaskLogger:
    """
    Logger that integrates with TaskLogCollector to provide real-time log reporting.
    """

    def __init__(self, collector: TaskLogCollector | None = None):
        self.collector = collector

    async def info(self, message: str) -> None:
        """Log info message."""
        logger.info(message)
        if self.collector:
            await self.collector.add_log(message, "info")

    async def warning(self, message: str) -> None:
        """Log warning message."""
        logger.warning(message)
        if self.collector:
            await self.collector.add_log(message, "warning")

    async def error(self, message: str) -> None:
        """Log error message."""
        logger.error(message)
        if self.collector:
            await self.collector.add_log(message, "error")

    async def debug(self, message: str) -> None:
        """Log debug message."""
        logger.debug(message)
        if self.collector:
            await self.collector.add_log(message, "debug")


class StreamLogHandler:
    """
    Handler for capturing stdout/stderr from subprocess and forwarding to TaskLogger.
    """

    def __init__(self, task_logger: TaskLogger):
        self.task_logger = task_logger

    async def handle_stream(self, stream: asyncio.StreamReader) -> None:
        """Handle stream output and forward to task logger."""
        while True:
            line = await stream.readline()
            if not line:
                break

            message = line.decode().strip()
            if message:  # Only log non-empty messages
                await self.task_logger.info(message)
