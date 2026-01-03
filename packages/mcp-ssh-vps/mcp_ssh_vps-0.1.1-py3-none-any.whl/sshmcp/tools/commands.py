"""MCP Tool for command execution."""

from typing import Any

import structlog

from sshmcp.config import get_machine
from sshmcp.security.audit import get_audit_logger
from sshmcp.security.validator import check_command_safety, validate_command
from sshmcp.ssh.client import SSHExecutionError
from sshmcp.ssh.pool import get_pool

logger = structlog.get_logger()


def execute_command(
    host: str,
    command: str,
    timeout: int | None = None,
) -> dict[str, Any]:
    """
    Execute a command on remote VPS server via SSH.

    This tool allows AI agents to execute commands on configured VPS servers
    with security validation and timeout protection.

    Args:
        host: Name of the host from machines.json configuration.
        command: Shell command to execute (must match whitelist patterns).
        timeout: Maximum execution time in seconds (default: from config).

    Returns:
        Dictionary with:
        - exit_code: Command exit code (0 = success)
        - stdout: Standard output text
        - stderr: Standard error text
        - duration_ms: Execution time in milliseconds
        - success: Boolean indicating success
        - host: Host where command was executed
        - command: The executed command

    Raises:
        ValueError: If host not found or command not allowed.
        RuntimeError: If SSH connection or execution fails.

    Example:
        >>> execute_command("production-server", "git pull origin main")
        {"exit_code": 0, "stdout": "Already up to date.", "stderr": "", ...}
    """
    audit = get_audit_logger()

    # Get machine configuration
    try:
        machine = get_machine(host)
    except Exception as e:
        audit.log(
            event="command_rejected",
            error=f"Host not found: {host}",
            metadata={"requested_host": host},
        )
        raise ValueError(f"Host not found: {host}") from e

    # Validate command against security rules
    is_valid, error_msg = validate_command(command, machine.security)
    if not is_valid:
        audit.log_command_rejected(host, command, error_msg or "Validation failed")
        raise ValueError(f"Command not allowed: {error_msg}")

    # Check for safety warnings
    warnings = check_command_safety(command)
    if warnings:
        logger.warning(
            "command_safety_warnings",
            host=host,
            command=command,
            warnings=warnings,
        )

    # Get timeout
    if timeout is None:
        timeout = machine.security.timeout_seconds

    # Execute command
    pool = get_pool()
    pool.register_machine(machine)

    try:
        client = pool.get_client(host)
        try:
            result = client.execute(command, timeout=timeout)

            audit.log_command_executed(
                host=host,
                command=command,
                exit_code=result.exit_code,
                duration_ms=result.duration_ms,
            )

            return result.to_dict()

        finally:
            pool.release_client(client)

    except SSHExecutionError as e:
        audit.log_command_failed(host, command, str(e))
        raise RuntimeError(f"Command execution failed: {e}") from e
    except Exception as e:
        audit.log_command_failed(host, command, str(e))
        raise RuntimeError(f"SSH error: {e}") from e
