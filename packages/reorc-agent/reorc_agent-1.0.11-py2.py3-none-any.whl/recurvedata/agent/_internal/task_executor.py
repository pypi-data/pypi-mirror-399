import asyncio
import base64
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from loguru import logger

from ..config import RECURVE_HOME
from .schemas import SourceCodeExecPayload, TaskResultPayload, TaskStatus
from .task_logger import StreamLogHandler, TaskLogCollector, TaskLogger


@dataclass
class TaskExecutor:
    """
    Task executor for source code execution.
    It will be used by task manager to execute source code tasks.
    The source code task was defined in the server side and transferred to the agent side.
    """

    task_heartbeat_interval: float = 1
    task_retry_interval: int = 5
    subprocess_pid: int | None = None

    def __init__(self, ws_connector: Any, message_id: str | None = None):
        self.ws_connector = ws_connector
        self.message_id = message_id

    async def execute(self, task: "SourceCodeExecPayload") -> "TaskResultPayload":
        start_time = time.time()
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.info(f"Task {task.task_instance_id} started in working directory: {temp_dir}")
            result = await self._execute_in_tempdir(task, temp_dir)

        logger.info(f"Task {task.task_instance_id} completed in {time.time() - start_time:.2f} seconds.")
        return result

    async def _execute_in_tempdir(self, task: "SourceCodeExecPayload", workdir: str) -> "TaskResultPayload":
        task_instance_id = task.task_instance_id

        cmd_args, output_file = self._prepare_execution_context(task, workdir)

        # Setup real-time log collection
        log_collector = TaskLogCollector(ws_connector=self.ws_connector, message_id=self.message_id)
        await log_collector.start()
        task_logger = TaskLogger(log_collector)

        try:
            await task_logger.info(f"Executing task: {task_instance_id}")

            await self.execute_in_subprocess(
                *cmd_args,
                cwd=workdir,
                timeout=task.max_duration,
                task_logger=task_logger,
            )

            # success, read result and update status
            result = None
            if output_file.exists():
                result = json.loads(output_file.read_text())

            await task_logger.info(f"Task {task_instance_id} completed successfully.")
            await log_collector.stop()

            return TaskResultPayload(status=TaskStatus.SUCCESS, result=result, error=None)
        except (subprocess.CalledProcessError, TimeoutError) as e:
            await task_logger.error(f"Task {task_instance_id} failed: {e}")
            await log_collector.stop()
            # raise for outside retry
            raise
        except Exception as e:
            await task_logger.error(f"Task {task_instance_id} failed: {e}")
            await log_collector.stop()

            return TaskResultPayload(
                status=TaskStatus.FAILED,
                error={"reason": str(e), "traceback": traceback.format_exc()},
                result=None,
            )

    @staticmethod
    def _prepare_execution_context(task: "SourceCodeExecPayload", workdir: str) -> tuple[tuple[str, ...], Path]:
        script = Path(workdir) / f"handler.{task.handler_format}"
        script.write_bytes(base64.b64decode(task.handler_code))

        input_file = Path(workdir) / "payload.json"
        input_file.write_text(json.dumps(task.payload, indent=2))

        output_file = Path(workdir) / "result.json"

        # python /path/to/handler.py --input /path/to/payload.json --output /path/to/result.json
        cmd_args = (
            str(script),
            "--input",
            str(input_file),
            "--output",
            str(output_file),
        )
        return cmd_args, output_file

    async def execute_in_subprocess(
        self,
        *args: str,
        cwd: str,
        timeout: int,
        task_logger: TaskLogger,
    ):
        env = os.environ.copy()
        env["RECURVE_HOME"] = RECURVE_HOME

        process = await asyncio.create_subprocess_exec(
            sys.executable,
            *args,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        self.subprocess_pid = process.pid
        try:
            # Use real-time log collection
            stream_handler = StreamLogHandler(task_logger)
            await asyncio.wait_for(
                asyncio.gather(
                    stream_handler.handle_stream(process.stdout),
                    stream_handler.handle_stream(process.stderr),
                ),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            logger.error(f"Subprocess timed out after {timeout} seconds, killing it.")
            process.kill()
            await process.wait()
            raise TimeoutError(f"Subprocess timed out after {timeout} seconds")

        rc = await process.wait()
        if rc < 0:
            signal_number = -rc
            signal_name = signal.Signals(signal_number).name
            msg = f"Subprocess was terminated by signal: {signal_name} (signal number: {signal_number})"
            logger.warning(msg)
            await task_logger.warning(msg)
        elif rc != 0:
            raise subprocess.CalledProcessError(rc, "python")
