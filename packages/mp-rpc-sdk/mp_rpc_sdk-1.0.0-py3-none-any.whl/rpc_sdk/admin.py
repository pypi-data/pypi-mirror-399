import requests
from typing import Any, Dict, List, Optional
from .exceptions import RPCError
class RPCAdmin:
    def __init__(
        self,
        endpoint: str,
        headers: Optional[dict] = None,
    ):
        self.endpoint = endpoint.rstrip('/')
        self.headers = headers or {}
    def list_nodes(
        self,
        env_type: Optional[str] = None,
        service: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        url = f"{self.endpoint}/admin/nodes"
        params = {}
        if env_type:
            params['env'] = env_type
        if service:
            params['service'] = service
        response = self._request('GET', url, params=params)
        return response.get('nodes', [])
    def get_node(self, node_id: str) -> Dict[str, Any]:
        url = f"{self.endpoint}/admin/nodes/{node_id}"
        return self._request('GET', url)
    def get_node_status(self, node_id: str) -> Dict[str, Any]:
        url = f"{self.endpoint}/admin/nodes/{node_id}/status"
        return self._request('GET', url)
    def delete_node(self, node_id: str) -> Dict[str, Any]:
        url = f"{self.endpoint}/admin/nodes/{node_id}"
        return self._request('DELETE', url)
    def list_services(self) -> List[Dict[str, Any]]:
        url = f"{self.endpoint}/admin/services"
        response = self._request('GET', url)
        return response.get('services', [])
    def _request(
        self,
        method: str,
        url: str,
        params: Optional[dict] = None,
        json: Optional[dict] = None,
    ) -> Dict[str, Any]:
        headers = {
            'Content-Type': 'application/json',
            **self.headers,
        }
        try:
            response = requests.request(
                method,
                url,
                params=params,
                json=json,
                headers=headers,
                timeout=30,
            )
            data = response.json()
            if response.status_code >= 400:
                error_msg = data.get('error', f'HTTP {response.status_code}')
                raise RPCError(error_msg)
            return data
        except requests.exceptions.Timeout:
            raise RPCError("Request timeout")
        except requests.exceptions.ConnectionError as e:
            raise RPCError(f"Connection error: {e}")
        except requests.exceptions.JSONDecodeError:
            raise RPCError(f"Invalid JSON response: {response.text}")
    def __repr__(self):
        return f"RPCAdmin(endpoint='{self.endpoint}')"