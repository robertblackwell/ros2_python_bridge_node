import time
import threading
import datetime
import time
from   serialio.configlinux import SerialConfig
from   bridgelib import FdQueue, SelectSerialBridge, detect_serial_port

def main():
    device = detect_serial_port()
    conf = SerialConfig()
    q = FdQueue()
    bridge = SelectSerialBridge(device, conf, q)
    t = threading.Thread(target=bridge.run, daemon=True)
    t.start()
    while True:
        time.sleep(1)
        dt = datetime.datetime.now().isoformat()
        bridge.send_message_thread_safe(f'echo 123 45 678 {dt}'.encode('utf-8'))
        while True:
            if q.queue.empty():
                print(f"did not get anything")
                break
            else:
                x = q.queue.get()
                print(f"got {x}")

main()