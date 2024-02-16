import os
import sys
import glob

import logging
from typing import List
import asyncio
from  serialio.configlinux import SerialConfig

from serialio.eventloop import SerialEventLoop

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from .transport_protocol import TransportProtocol

from .transport_lf import Transport_LF

from .client_queue_protocol import ClientQueueProtocol


def detect_serial_port() -> str:
    r: List[str] = glob.glob("/dev/ttyACM*")
    if type(r) is list and len(r) == 1:
        print(f"found serial port: {r[0]} ")
        return r[0]
    raise RuntimeError(f"Error finding serial port")

class SerialBridge:

    def __init__(self,
                 device: str, 
                 conf: SerialConfig,
                 client_queue: ClientQueueProtocol
                 ):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.loop: asyncio.AbstractEventLoop = loop
        self.work_queue: asyncio.Queue = asyncio.Queue()
        self.serial: SerialEventLoop = SerialEventLoop(device, conf, loop)
        self.transport: TransportProtocol = Transport_LF(self.serial)
        self.client_queue = client_queue

    def send_message_thread_safe(self, msg: bytes):
        """
        Puts a work queue entry on the work queue from another thread.
        This is how another thread gets the pico_agent to do something for it
        """
        logging.info(f"send_queue_entry {msg.decode('utf-8')}")
        asyncio.run_coroutine_threadsafe(self._queue_command(msg), self.loop)

    def run(self):
        try:
            self.loop.run_until_complete(self._co_main())
        except Exception as e:
            logging.warn("exception in loop.run_forever()")

    # below here private

    async def _queue_command(self, msg: bytes):
        logging.info(f"_queue_command {msg.decode('utf-8')}")
        await self.work_queue.put(msg)


    async def _co_main(self):

        async def writer():
            logging.info(f"check_queue entered {self} queue: {id(self.work_queue)}")
            count = 0
            while True:
                logging.info("Check work queue")
                msg: bytes = await self.work_queue.get()
                await self.transport.write_message(msg)
                logging.info(f"Check work queue got one line {msg.decode('utf-8')}")

        async def reader():
            while True:
                msg = await self.transport.read_message()
                self.client_queue.put_nowait(msg)


        reader_task = asyncio.create_task(reader())
        writer_task = asyncio.create_task(writer())
        await reader_task
        await writer_task
