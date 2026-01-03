"""SSH connection pool for managing multiple connections."""

import threading
import time
from typing import TYPE_CHECKING, Dict, Optional

import structlog

from sshmcp.models.machine import MachineConfig

if TYPE_CHECKING:
    from sshmcp.models.machine import MachinesConfig
from sshmcp.ssh.client import SSHClient, SSHConnectionError

logger = structlog.get_logger()


class SSHConnectionPool:
    """
    Pool for managing SSH connections to multiple servers.

    Provides connection reuse and automatic cleanup of idle connections.
    """

    def __init__(
        self,
        max_connections_per_host: int = 3,
        idle_timeout: int = 300,  # 5 minutes
    ) -> None:
        """
        Initialize connection pool.

        Args:
            max_connections_per_host: Maximum connections per host.
            idle_timeout: Time in seconds before idle connections are closed.
        """
        self.max_connections_per_host = max_connections_per_host
        self.idle_timeout = idle_timeout

        self._connections: Dict[str, list[tuple[SSHClient, float]]] = {}
        self._lock = threading.Lock()
        self._machines: Dict[str, MachineConfig] = {}

    def register_machine(self, machine: MachineConfig) -> None:
        """
        Register a machine configuration.

        Args:
            machine: Machine configuration to register.
        """
        with self._lock:
            self._machines[machine.name] = machine
            if machine.name not in self._connections:
                self._connections[machine.name] = []

        logger.info("pool_machine_registered", machine=machine.name)

    def get_client(self, name: str) -> SSHClient:
        """
        Get an SSH client for the specified machine.

        Returns an existing connection if available, or creates a new one.

        Args:
            name: Machine name.

        Returns:
            SSHClient connected to the machine.

        Raises:
            SSHConnectionError: If machine not found or connection fails.
        """
        with self._lock:
            if name not in self._machines:
                raise SSHConnectionError(f"Machine not registered: {name}")

            machine = self._machines[name]

            # Try to get an existing connection
            if name in self._connections:
                connections = self._connections[name]
                while connections:
                    client, last_used = connections.pop(0)
                    if client.is_connected:
                        logger.debug("pool_reusing_connection", machine=name)
                        return client
                    else:
                        # Connection was closed, discard it
                        try:
                            client.disconnect()
                        except Exception:
                            pass

            # Create new connection
            logger.info("pool_creating_connection", machine=name)
            client = SSHClient(machine)
            client.connect()
            return client

    def release_client(self, client: SSHClient) -> None:
        """
        Return a client to the pool for reuse.

        Args:
            client: SSHClient to release.
        """
        name = client.machine.name

        with self._lock:
            if name not in self._connections:
                self._connections[name] = []

            connections = self._connections[name]

            # Check if we have room for more connections
            if len(connections) < self.max_connections_per_host:
                if client.is_connected:
                    connections.append((client, time.time()))
                    logger.debug("pool_connection_released", machine=name)
                    return

            # Pool is full or connection is dead, close it
            try:
                client.disconnect()
            except Exception:
                pass

    def cleanup_idle(self) -> int:
        """
        Close connections that have been idle too long.

        Returns:
            Number of connections closed.
        """
        closed = 0
        current_time = time.time()

        with self._lock:
            for name, connections in self._connections.items():
                active = []
                for client, last_used in connections:
                    if current_time - last_used > self.idle_timeout:
                        try:
                            client.disconnect()
                            closed += 1
                        except Exception:
                            pass
                    else:
                        active.append((client, last_used))
                self._connections[name] = active

        if closed > 0:
            logger.info("pool_cleanup", closed_connections=closed)

        return closed

    def close_all(self) -> None:
        """Close all connections in the pool."""
        with self._lock:
            for name, connections in self._connections.items():
                for client, _ in connections:
                    try:
                        client.disconnect()
                    except Exception:
                        pass
                connections.clear()

        logger.info("pool_closed_all")

    def get_stats(self) -> dict:
        """
        Get pool statistics.

        Returns:
            Dictionary with pool statistics.
        """
        with self._lock:
            stats = {
                "machines": len(self._machines),
                "connections": {},
            }
            for name, connections in self._connections.items():
                active = sum(1 for c, _ in connections if c.is_connected)
                stats["connections"][name] = {
                    "total": len(connections),
                    "active": active,
                }
            return stats


# Global connection pool instance
_pool: Optional[SSHConnectionPool] = None


def get_pool() -> SSHConnectionPool:
    """Get or create the global connection pool."""
    global _pool
    if _pool is None:
        _pool = SSHConnectionPool()
    return _pool


def init_pool(config: "MachinesConfig") -> SSHConnectionPool:  # type: ignore
    """
    Initialize the global connection pool with machines from config.

    Args:
        config: MachinesConfig with machine definitions.

    Returns:
        Initialized SSHConnectionPool.
    """

    pool = get_pool()
    for machine in config.machines:
        pool.register_machine(machine)
    return pool
