from typing import Protocol, Any, Optional

class ClientQueueProtocol(Protocol):
    """
    This protocol intends to represent things like queue.Queue but with maybe some added functionality.

    In particular using a pipe to interact with tasks that use select.select to wait for things to do.

    put_nowait - should not raise an exception as part of normal operation and should no wait 

    get_nowait - should not raise exceptions as part of normal operation and should not wait

    """
    
    def put_nowait(self, item: Any) -> None:
        ... 

    def get_nowait(self) -> Optional[Any]:
        ...