import os
import sys
import glob
import time
import datetime
import logging
import select
from typing import List, Optional
from  serialio.configlinux import SerialConfig

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from .client_queue_protocol import ClientQueueProtocol
from .fdqueue import FdQueue

def detect_serial_port() -> str:
    r: List[str] = glob.glob("/dev/ttyACM*")
    if type(r) is list and len(r) == 1:
        print(f"found serial port: {r[0]} ")
        return r[0]
    raise RuntimeError(f"Error finding serial port")

class SelectSerialBridge:
    """
    This class provides similar functionality to SrialBridge but does not use asyncio
    but rather resorts to select.select in a very old-school style
    """
    def __init__(self,
                 device: str, 
                 conf: SerialConfig,
                 client_queue: ClientQueueProtocol
                 ):
        self._fd = os.open(device, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)  
        self.config = conf
        self.config.apply(device, self._fd)
        os.set_blocking(self._fd, False)
        self.read_size = 512
        self.read_buffer: bytearray = bytearray(b'')

        # self.work_queue: asyncio.Queue = asyncio.Queue()
        self.client_queue = client_queue
        self.output_queue = FdQueue()

        self.read_set, self.write_set, self.except_set = [], [], []
        self.write_buffer : Optional[bytes] = None

    def send_message_thread_safe(self, msg: bytes):
        self.output_queue.put_nowait(msg)

    def run(self):
        self.read_set = [self._fd, self.output_queue]
        self.write_set = []
        self.except_set = [self._fd]
        while True:
            try:
                x, y, z = select.select(self.read_set, self.write_set, self.except_set)
                if len(z) != 0:
                    pass
                self.try_write()
                if self._fd in x:
                    self.read_data()
            except BlockingIOError as be:
                raise be
            except OSError as e:
                print(f"OSerror {e}")
                raise e



    def try_write(self):

        if self.write_buffer is None:
            if not self.output_queue.empty():
                msg = self.output_queue.get_nowait()
                self.write_buffer = msg + b'\n'
            else:
                pass
        if self.write_buffer is not None:
            # a write operation is in progress
            try:
                n = os.write(self._fd, self.write_buffer)
                if n == len(self.write_buffer):
                    self.write_buffer = None
                elif n > 0:
                    self.write_buffer = self.write_buffer[n:]
                else:
                    pass
            except BlockingIOError as be:
                raise be
                pass
            except OSError as ose:
                raise ose
                pass        
        if self._fd in self.write_set:
            self.write_set.remove(self._fd)
        if self.write_buffer is not None:
            self.write_set.append(self._fd)

    def read_data(self):
        """ Try and read some data"""
        LF=ord('\n')
        CR=ord('\r')
        byts = os.read(self._fd, self.read_size)
        buf = bytearray(byts)
        if len(buf) == 0:
            return
        for b in buf:
            if b == CR:
                pass
            elif b == LF:
                self.client_queue.put_nowait(self.read_buffer[0:])
                self.read_buffer = bytearray(b'')
            else:
                self.read_buffer.append(b)

