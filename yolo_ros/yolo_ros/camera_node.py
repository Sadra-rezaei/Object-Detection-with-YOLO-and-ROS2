
import cv2

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


class CameraNode(Node):
    def __init__(self):
        super().__init__('camera_node')

        self.declare_parameter(
            'camera_url',
            'http://192.168.1.5:8080/video'
        )
        self.declare_parameter('fps', 10.0)

        camera_url = self.get_parameter('camera_url').value
        fps = float(self.get_parameter('fps').value)

        self.bridge = CvBridge()
        self.publisher = self.create_publisher(
            Image,
            '/camera/image_raw',
            qos_profile_sensor_data
        )

        self.cap = cv2.VideoCapture(camera_url)

        if not self.cap.isOpened():
            raise RuntimeError(
                f'Cannot open camera stream: {camera_url}'
            )

        period = 1.0 / max(fps, 0.1)
        self.timer = self.create_timer(period, self.publish_frame)

        self.get_logger().info(
            f'Camera connected: {camera_url}'
        )
        self.get_logger().info(
            'Publishing images on /camera/image_raw'
        )

    def publish_frame(self):
        ret, frame = self.cap.read()

        if not ret or frame is None:
            self.get_logger().warning(
                'Failed to read camera frame'
            )
            return

        msg = self.bridge.cv2_to_imgmsg(
            frame,
            encoding='bgr8'
        )
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'phone_camera'

        self.publisher.publish(msg)

    def destroy_node(self):
        if hasattr(self, 'cap') and self.cap is not None:
            self.cap.release()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = None

    try:
        node = CameraNode()
        rclpy.spin(node)
    except (RuntimeError, KeyboardInterrupt) as exc:
        if isinstance(exc, RuntimeError):
            print(f'Camera node error: {exc}')
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
