import logging
import os
import sys
from .transport_protocol import TransportProtocol

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from serialio.configlinux import SerialConfig
from serialio.eventloop import SerialEventLoop


class Transport_LF(TransportProtocol):

    def __init__(self, serial: SerialEventLoop):
        self.serial = serial
        self.byte_buffer: bytes = b''

    async def read_message(self) -> bytes:
        """
        This function waits for and reads incoming messages and yields them to a caller
        """
        processed_buffer = bytearray(b'')
        while True:
            if len(self.byte_buffer) == 0:
                self.byte_buffer = await self.serial.co_read()
                logging.debug(f"transport_ln {self.byte_buffer}")
                
            for ix in range(0, len(self.byte_buffer)):
            # for onebyte in self.byte_buffer:
                onebyte = self.byte_buffer[ix]
                ch = chr(onebyte)
                if ch == '\n':
                    self.byte_buffer = self.byte_buffer[ix+1:]
                    logging.debug(f"transport_ln about to return {processed_buffer} leaving {self.byte_buffer}")
                    return bytes(processed_buffer)
                elif ch == '\r':
                    pass
                else:
                    processed_buffer.append(onebyte)
            logging.debug(f"transport_ln loop has ended byte_buffer: {self.byte_buffer} ")
            self.byte_buffer = bytearray(b'')
    
    async def write_message(self, message: bytes):
        m = message.decode('utf-8')
        await self.serial.co_write(f"{m}\n".encode('utf-8'))
