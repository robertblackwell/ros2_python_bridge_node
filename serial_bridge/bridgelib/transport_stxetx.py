import logging
import os
import sys
from typing import Optional, Dict
import json
from .transport_protocol import TransportProtocol

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from serialio.configlinux import SerialConfig
from serialio.eventloop import SerialEventLoop


def parse_message(message: bytes) -> Optional[Dict]:
    try:
        d = json.loads(message.decode('utf-8'))
    except json.JSONDecodeError as e:
        return None
    return d



class Transport_stxetx(TransportProtocol):

    def __init__(self, serial: SerialEventLoop):
        self.serial = serial


    async def read_message(self) -> bytes:
        """
        This function waits for and reads incoming messages and yields them to a caller
        """
        STX = '\x02'
        ETX = '\x03'
        buffer = ''
        line_buffer = ''
        state = 0
        while True:
            b = await self.serial.co_read()
            for ch in b.decode('utf-8'):
                if state == 0:
                    if ch == STX:
                        state = 1
                elif state == 1:
                    if ch == ETX:
                        state = 0
                        return buffer[1:].encode('utf-8')
                    else:
                        if ch == STX:
                            raise RuntimeError(f"ERROR STX while collecting bytes")
                        buffer += ch
            pass

    async def write_message(self, message: bytes):
        STX = '\x02'
        ETX = '\x03'
        m = message.decode('utf-8')
        await self.serial.co_write(f"{STX}1{m}{ETX}".encode('utf-8'))

