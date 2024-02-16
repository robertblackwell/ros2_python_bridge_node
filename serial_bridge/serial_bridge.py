import time
import os
import sys
import datetime
import queue
import threading
from typing import Any, Optional
from example_interfaces.msg import String
def ros2_run_syspath_setup():
    import sys
    def ros2_get_package_name_and_src():
        dir1 = os.path.dirname(__file__)
        dir2 = os.path.dirname(dir1)
        src_dir = os.path.dirname(dir2)
        d1 = os.path.basename(dir1)
        d2 = os.path.basename(dir2)
        if d1 != d2:
            raise AssertionError(f"something went wrong d1:{d1} and d2:{d2} should be the same for a ros2 package")
        return d1, src_dir

    pkg_name, src_dir = ros2_get_package_name_and_src()
    rv = [os.path.join(src_dir, f"build/{pkg_name}")] + [p for p in sys.path if (f"src/{pkg_name}" not in p) and ("src/build" not in p)]

    return rv

if __name__ == "__main__":
    print("running direct invocation")
    sys.path = ros2_run_syspath_setup()
else:
    print(f"running under ros2 run __name__:{__name__}")

from serial_bridge.mysubpackage.myclass import MyClass
from serial_bridge.mysubpackage.myfunctions import myfunction

import rclpy
from rclpy.node import Node, GuardCondition

class GuardConditionQueue:
    def __init__(self, guard_condition: GuardCondition):
        self.queue: queue.Queue = queue.Queue()
        self.guard_condition = guard_condition

    def put_nowait(self, item):
        self.queue.put_nowait(item)
        self.guard_condition.trigger()

    def get_nowait(self) -> Any:
        try:
            item = self.queue.get_nowait()
            return item
            pass
        except queue.Empty as e:
            return None
        except Exception as e:
            print(f"Exception {e}")


class Bridge(Node):
    def __init__(self):
        super().__init__('print_forever')
        self.myclass = MyClass("This is the initial string")
        timer_period = 5
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.publisher = self.create_publisher(String, "bridge_publisher", 10)
        self.guard_condition = self.create_guard_condition(self.guard_callback)
        self.guard_queue = GuardConditionQueue(self.guard_condition)
        self.print_count = 0

    def guard_callback(self):
        item = self.guard_queue.get_nowait()
        self.get_logger().info(f"YYYYYYguard_callback entered item:{item}")
        msg = String()
        msg.data = f"YYYYYYguard_callback entered item:{item}"

        self.publisher.publish(msg)

    def timer_callback(self):
        self.get_logger().info(f'Printed {self.print_count} times')
        self.get_logger().info(f"myfunction: {myfunction()}  myclass.mymethod: {self.myclass.mymethod()}")
        self.print_count += 1

def thread_main(guard_queue: GuardConditionQueue):
    while True:
        time.sleep(2.0)
        print("background thread")
        text = datetime.datetime.now().isoformat()
        guard_queue.put_nowait(f"guard queue item {text}")

def main(args=None):
    # myclass = MyClass("this is the initial string value")
    # while True:
    #     print(f"myfunction: {myfunction()}  myclass.mymethod: {myclass.mymethod()}")
    #     time.sleep(3)
    try:
        rclpy.init(args=args)
        bridge_node = Bridge()

        t = threading.Thread(target=thread_main, args=[bridge_node.guard_queue], daemon=True)
        t.start()
        rclpy.spin(bridge_node)

    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)


main()
