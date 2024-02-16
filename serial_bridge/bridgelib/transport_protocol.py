import logging
import os
import sys
from typing import Protocol

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from serialio.configlinux import SerialConfig
from serialio.eventloop import SerialEventLoop

class TransportProtocol(Protocol):
    def __init__(self, serial: SerialEventLoop):
        ...

    async def read_message(self) -> bytes:
        ...

    async def write_message(self, message: bytes):
        ...

