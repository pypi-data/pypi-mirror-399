class RPCError(Exception):
    def __init__(self, message, code=None, data=None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.data = data
    def __str__(self):
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message
class NodeNotFoundError(RPCError):
    def __init__(self, node_id):
        super().__init__(f"Node {node_id} not found", code=-32001)
        self.node_id = node_id
class NodeOfflineError(RPCError):
    def __init__(self, node_id):
        super().__init__(f"Node {node_id} is offline", code=-32002)
        self.node_id = node_id
class TimeoutError(RPCError):
    def __init__(self, timeout):
        super().__init__(f"Request timeout after {timeout}ms", code=-32003)
        self.timeout = timeout
class MethodNotFoundError(RPCError):
    def __init__(self, method):
        super().__init__(f"Method {method} not found", code=-32601)
        self.method = method
class ExecutionError(RPCError):
    def __init__(self, message, data=None):
        super().__init__(message, code=-32603, data=data)
ERROR_CODE_MAP = {
    -32001: NodeNotFoundError,
    -32002: NodeOfflineError,
    -32003: TimeoutError,
    -32601: MethodNotFoundError,
    -32603: ExecutionError,
}
def raise_for_error(response):
    if response.get('success'):
        return
    error = response.get('error', {})
    code = error.get('code', -32603)
    message = error.get('message', 'Unknown error')
    data = error.get('data')
    error_class = ERROR_CODE_MAP.get(code, RPCError)
    if error_class == NodeNotFoundError:
        raise NodeNotFoundError(message.split()[-1] if 'not found' in message else 'unknown')
    elif error_class == NodeOfflineError:
        raise NodeOfflineError(message.split()[1] if 'offline' in message else 'unknown')
    elif error_class == TimeoutError:
        raise TimeoutError(30000)
    elif error_class == MethodNotFoundError:
        raise MethodNotFoundError(message.split()[-1] if 'not found' in message else 'unknown')
    else:
        raise RPCError(message, code=code, data=data)