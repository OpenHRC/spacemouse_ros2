import rclpy
from rclpy.node import Node
# from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy
from std_msgs.msg import Float32
import pyspacemouse


class SpaceMousePublisher(Node):
    """
    A ROS2 Node that publishes 3D mouse input as Twist messages.

    This class initializes a ROS2 publisher to publish geometry_msgs/Twist messages
    based on the input from a 3D SpaceMouse device. It uses the pyspacemouse library
    to read the device state and publishes the corresponding linear and angular
    velocities at a fixed rate.
    """

    def __init__(self):
        super().__init__("spacemouse_publisher")
        self.get_logger().info("Initializing SpaceMouse publisher...")

        self.declare_parameter("operator_position_front", True)
        self._operator_position_front = (
            self.get_parameter("operator_position_front").get_parameter_value().bool_value
        )
        self.get_logger().info(f"Operator position front: {self._operator_position_front}")

        self.declare_parameter("device_path", "")
        self._device_path = self.get_parameter("device_path").get_parameter_value().string_value

        self._joy_publisher = self.create_publisher(
            Joy, "joy", 10
        )

        if self._device_path == "":
            self.device = pyspacemouse.open()
        else:
            self.device = pyspacemouse.open_by_path(self._device_path)

        self._timer = self.create_timer(0.01, self._timer_callback)

    def __del__(self):
        if self.device is not None:
            self.device.close()

    def _timer_callback(self):
        if self.device is not None:
            state = self.device.read()

            joy_msg = Joy()
            joy_msg.axes = [
                float(state.y),
                -float(state.x),
                float(state.z),
                float(state.roll),
                float(state.pitch),
                -float(state.yaw),
            ]
            joy_msg.buttons = state.buttons

            self._joy_publisher.publish(joy_msg)


def main(args=None):
    rclpy.init(args=args)
    spacemouse_publisher = SpaceMousePublisher()
    rclpy.spin(spacemouse_publisher)
    spacemouse_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
