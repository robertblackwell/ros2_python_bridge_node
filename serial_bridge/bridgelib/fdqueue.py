import queue
import os
from typing import Any


class FdQueue:
    """
    This class is an interthread queue that can be waited upon with select.
    It uses a wellknown Linux/Unix trick to wake a thread waiting on a select call
    It allows a thread reading data from a serial port to provid input to another
    thread that is using curses.getch() to get keyboard input.
    
    """

    def __init__(self):
        self.queue = queue.Queue()
        self.r, self.w = os.pipe()
        os.set_blocking(self.r, False)
        self.rfile = os.fdopen(self.r)
        self.wfile = os.fdopen(self.w)
        self._fileno = self.r

    def fileno(self):
        return self._fileno
    
    def put_nowait(self, item: Any):
        self.queue.put_nowait(item)
        os.write(self.w, b"X")

    def get_nowait(self) -> Any:
        if self.queue.empty():
            return None
        tmp = os.read(self.r, 1)
        try:
            item = self.queue.get_nowait()
        except queue.Empty as e:
            return None

        return item
    
    def empty(self):
        return self.queue.empty()