import requests
from typing import Any, List, Optional
from .exceptions import RPCError, raise_for_error
from .agent import AgentCapabilities
class RPCClient:
    def __init__(
        self,
        endpoint: str,
        node: str,
        timeout: int = 30000,
        headers: Optional[dict] = None,
    ):
        self.endpoint = endpoint.rstrip('/')
        self.node = node
        self.timeout = timeout
        self.headers = headers or {}
        self.agent = AgentCapabilities(self)
    def call(
        self,
        method: str,
        params: Optional[List[Any]] = None,
        timeout: Optional[int] = None,
    ) -> Any:
        if params is None:
            params = []
        request_timeout = timeout or self.timeout
        url = f"{self.endpoint}/rpc/call"
        payload = {
            'nodeId': self.node,
            'method': method,
            'params': params,
            'timeout': request_timeout,
        }
        headers = {
            'Content-Type': 'application/json',
            **self.headers,
        }
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=request_timeout / 1000 + 5,
            )
            if response.status_code >= 400:
                try:
                    data = response.json()
                    raise_for_error(data)
                except requests.exceptions.JSONDecodeError:
                    raise RPCError(f"HTTP {response.status_code}: {response.text}")
            data = response.json()
            raise_for_error(data)
            return data.get('result')
        except requests.exceptions.Timeout:
            raise RPCError(f"Request timeout after {request_timeout}ms", code=-32003)
        except requests.exceptions.ConnectionError as e:
            raise RPCError(f"Connection error: {e}", code=-32000)
    def __repr__(self):
        return f"RPCClient(endpoint='{self.endpoint}', node='{self.node}')"