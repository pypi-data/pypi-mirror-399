"""
RPC SDK - Python client for Browser RPC System

Usage:
    from rpc_sdk import RPCClient, RPCAdmin
    
    # Business calls
    client = RPCClient(
        endpoint='https://rpc-gateway.pub2022.workers.dev',
        node='browser-abc123'
    )
    
    # Call platform methods
    profile = client.call('douyin.getUserProfile', ['user123'])
    client.call('facebook.post', ['Hello World'])
    
    # Browser capabilities
    client.agent.setCookies('douyin.com', cookies)
    tabs = client.agent.getTabs()
    
    # Admin operations
    admin = RPCAdmin(endpoint='https://rpc-gateway.pub2022.workers.dev')
    nodes = admin.list_nodes()
    status = admin.get_node_status('browser-abc123')
"""

from .client import RPCClient
from .admin import RPCAdmin
from .agent import AgentCapabilities
from .exceptions import (
    RPCError,
    NodeNotFoundError,
    NodeOfflineError,
    TimeoutError,
    MethodNotFoundError,
    ExecutionError,
)

__version__ = '1.0.0'
__all__ = [
    'RPCClient',
    'RPCAdmin',
    'AgentCapabilities',
    'RPCError',
    'NodeNotFoundError',
    'NodeOfflineError',
    'TimeoutError',
    'MethodNotFoundError',
    'ExecutionError',
]
