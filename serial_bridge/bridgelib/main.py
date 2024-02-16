import os
import sys
import logging
import threading
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from serialio.configlinux import SerialConfig
from serialio.eventloop import SerialEventLoop
from closed_loop_control import TwoMotorController

import pico_simple_bridge
# from pico_simple_bridge import PicoSimpleBridge, detect_serial_port
# from pico_simple_bridge import Transport_LF
# from pico_simple_bridge import LineReaderThread

def main(serial_path, conf: SerialConfig):
    #
    # Note where the log file is located. Use a file so that the log output does
    #  not get in the way of the keyboard input. Watch the logfile in realtime with
    #  `tail -f host_log`
    #
    logging.basicConfig(filename=os.path.join(os.path.dirname(__file__), "host_log"), level=logging.DEBUG)
    loop = asyncio.new_event_loop()
    serial = SerialEventLoop(serial_path, conf, loop)
    transport = pico_simple_bridge.Transport_LF(serial)
    agent = pico_simple_bridge.PicoSimpleBridge(loop, serial, transport)

    #
    # Now start a thread that reads and parses keyboard commands and hands them off
    # to the PicoAgent to be sent to the microcontroller. Note this new thread
    # needs to have access to the 'agent'
    #
    cli_input_thread = pico_simple_bridge.LineReaderThread(agent)
    t = threading.Thread(target=cli_input_thread.handle_keyboard_commands, args=[], daemon=True)
    t.start()

    loop.run_until_complete(agent.co_main())
    t.join()


if __name__ == "__main__":
    p = detect_serial_port()
    main(p, SerialConfig())
