import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from .serial_bridge import SerialBridge


class LineReaderThread:
    def __init__(self, agent: SerialBridge):
        self.agent = agent
        pass

    def handle_keyboard_commands(self):
        while True:
            line = input("Please enter a command: \n")
            self.agent.send_message_thread_safe(line.encode('utf-8'))
