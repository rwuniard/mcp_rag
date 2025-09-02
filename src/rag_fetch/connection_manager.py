"""
Connection management for MCP RAG Server.

Handles tracking and monitoring of multiple HTTP client connections.
"""

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, Set
import logging

logger = logging.getLogger(__name__)


@dataclass
class ConnectionInfo:
    """Information about a client connection."""
    id: str
    client_ip: str
    user_agent: str
    connected_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    requests_count: int = 0
    
    @property
    def duration(self) -> float:
        """Get connection duration in seconds."""
        return time.time() - self.connected_at
    
    @property
    def idle_time(self) -> float:
        """Get idle time in seconds since last activity."""
        return time.time() - self.last_activity
    
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = time.time()
        self.requests_count += 1


class ConnectionManager:
    """Manages HTTP client connections and metrics."""
    
    def __init__(self, max_connections: int = 100, connection_timeout: int = 300):
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        self.connections: Dict[str, ConnectionInfo] = {}
        self.metrics = {
            "total_connections": 0,
            "current_connections": 0,
            "failed_connections": 0,
            "timed_out_connections": 0,
            "rejected_connections": 0,
        }
        
    def create_connection(self, client_ip: str, user_agent: str = "unknown") -> str:
        """
        Create a new connection.
        
        Args:
            client_ip: Client IP address
            user_agent: Client User-Agent string
            
        Returns:
            Connection ID if successful
            
        Raises:
            ConnectionError: If max connections exceeded
        """
        # Check connection limit
        if len(self.connections) >= self.max_connections:
            self.metrics["rejected_connections"] += 1
            raise ConnectionError(f"Maximum connections ({self.max_connections}) exceeded")
        
        # Cleanup timed out connections
        self._cleanup_timed_out_connections()
        
        # Create new connection
        connection_id = str(uuid.uuid4())
        connection = ConnectionInfo(
            id=connection_id,
            client_ip=client_ip,
            user_agent=user_agent
        )
        
        self.connections[connection_id] = connection
        self.metrics["total_connections"] += 1
        self.metrics["current_connections"] = len(self.connections)
        
        logger.info(f"New connection: {connection_id} from {client_ip}")
        return connection_id
    
    def get_connection(self, connection_id: str) -> ConnectionInfo:
        """Get connection info by ID."""
        if connection_id not in self.connections:
            raise KeyError(f"Connection {connection_id} not found")
        return self.connections[connection_id]
    
    def update_connection_activity(self, connection_id: str):
        """Update connection activity timestamp."""
        if connection_id in self.connections:
            self.connections[connection_id].update_activity()
    
    def close_connection(self, connection_id: str):
        """Close a connection."""
        if connection_id in self.connections:
            connection = self.connections[connection_id]
            duration = connection.duration
            requests = connection.requests_count
            
            del self.connections[connection_id]
            self.metrics["current_connections"] = len(self.connections)
            
            logger.info(
                f"Connection closed: {connection_id}, "
                f"duration: {duration:.1f}s, requests: {requests}"
            )
    
    def _cleanup_timed_out_connections(self):
        """Remove connections that have timed out."""
        current_time = time.time()
        timed_out_connections = []
        
        for connection_id, connection in self.connections.items():
            if current_time - connection.last_activity > self.connection_timeout:
                timed_out_connections.append(connection_id)
        
        for connection_id in timed_out_connections:
            logger.warning(f"Connection timed out: {connection_id}")
            self.close_connection(connection_id)
            self.metrics["timed_out_connections"] += 1
    
    def get_active_connections(self) -> Dict[str, dict]:
        """Get information about all active connections."""
        self._cleanup_timed_out_connections()
        
        active = {}
        for connection_id, connection in self.connections.items():
            active[connection_id] = {
                "client_ip": connection.client_ip,
                "user_agent": connection.user_agent,
                "connected_at": connection.connected_at,
                "duration": connection.duration,
                "idle_time": connection.idle_time,
                "requests_count": connection.requests_count,
            }
        
        return active
    
    def get_metrics(self) -> dict:
        """Get connection metrics."""
        self._cleanup_timed_out_connections()
        metrics = self.metrics.copy()
        metrics["current_connections"] = len(self.connections)
        return metrics
    
    def shutdown(self):
        """Shutdown connection manager and close all connections."""
        logger.info(f"Shutting down connection manager, closing {len(self.connections)} connections")
        connection_ids = list(self.connections.keys())
        for connection_id in connection_ids:
            self.close_connection(connection_id)


# Global connection manager instance
connection_manager = ConnectionManager()