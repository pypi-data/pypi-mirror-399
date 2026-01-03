import os

import typer

from .._internal.agent import Agent
from ..exceptions import UnauthorizedError
from ._typer import RecurveTyper, exit_with_error

agent_app = RecurveTyper(help="Commands for interacting with the agent.")


@agent_app.command()
async def start():
    """Start the agent."""

    agent = Agent.default()
    exit_code = 0  # Default to success (normal shutdown)
    try:
        if not agent.has_logged_in:
            exit_with_error("Agent not logged in.")

        _check_environment()

        # TODO(yangliang): setup signal handlers

        pid = os.getpid()
        typer.secho(f"Agent {agent.id} started with PID {pid}.", fg="green")

        try:
            await agent.start()
            typer.echo("Agent stopped.")
        except UnauthorizedError:
            typer.secho("Unauthorized, please re-login with a valid token.", fg="red")
        except KeyboardInterrupt:
            typer.secho("Agent stopped by user.", fg="yellow")
        except Exception as e:
            typer.secho(f"Agent stopped due to error: {e}", fg="red")
            # set exit code to 1 to signal error to systemd for restart
            exit_code = 1
            raise
    finally:
        # always close httpx.AsyncClient
        await agent.close()
        # Ensure all logs are written before exit
        from loguru import logger

        logger.info("Shutting down agent...")
        logger.complete()  # Wait for log queue to be flushed
        # Force exit to ensure process terminates, avoiding hanging tasks in event loop
        # Use os._exit() instead of sys.exit() to bypass asyncio cleanup and ensure immediate termination
        # Use non-zero exit code for errors so systemd will restart the service
        os._exit(exit_code)


def _check_environment():
    _check_host_info()
    _check_dockerd()
    _check_docker_compose()


def _check_dockerd():
    import docker

    try:
        client = docker.from_env()
        client.ping()
    except Exception as e:
        exit_with_error(f"Failed to connect to Docker: {e}")


def _check_docker_compose():
    import subprocess

    try:
        subprocess.run(
            ["docker", "compose"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        exit_with_error("docker compose is not installed.")


def _check_host_info():
    from .._internal.host import get_hostname_ip

    try:
        get_hostname_ip()
    except Exception as e:
        exit_with_error(str(e))
