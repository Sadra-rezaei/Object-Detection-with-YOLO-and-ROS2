
import json

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge

from ultralytics import YOLO


class DetectionNode(Node):
    def __init__(self):
        super().__init__('yolo_detection_node')

        self.declare_parameter('model', 'yolo11n.pt')
        self.declare_parameter('confidence', 0.5)

        model_path = self.get_parameter('model').value
        self.confidence = float(
            self.get_parameter('confidence').value
        )

        self.bridge = CvBridge()
        self.model = YOLO(model_path)

        self.publisher = self.create_publisher(
            String,
            '/yolo/detections',
            10
        )

        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            qos_profile_sensor_data
        )

        self.get_logger().info(
            f'YOLO model loaded: {model_path}'
        )
        self.get_logger().info(
            'Publishing detections on /yolo/detections'
        )

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding='bgr8'
            )

            results = self.model.predict(
                source=frame,
                conf=self.confidence,
                verbose=False
            )

            detections = []

            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls[0].item())
                    class_name = result.names[class_id]
                    confidence = float(box.conf[0].item())

                    x1, y1, x2, y2 = [
                        int(value)
                        for value in box.xyxy[0].tolist()
                    ]

                    detections.append({
                        'class_id': class_id,
                        'class_name': class_name,
                        'confidence': round(confidence, 4),
                        'bbox': {
                            'x1': x1,
                            'y1': y1,
                            'x2': x2,
                            'y2': y2
                        }
                    })

            output = {
                'stamp': {
                    'sec': msg.header.stamp.sec,
                    'nanosec': msg.header.stamp.nanosec
                },
                'frame_id': msg.header.frame_id,
                'detections': detections
            }

            output_msg = String()
            output_msg.data = json.dumps(
                output,
                ensure_ascii=False
            )

            self.publisher.publish(output_msg)

        except Exception as exc:
            self.get_logger().error(
                f'Detection error: {exc}'
            )


def main(args=None):
    rclpy.init(args=args)
    node = None

    try:
        node = DetectionNode()
        rclpy.spin(node)
    except (KeyboardInterrupt, Exception) as exc:
        if not isinstance(exc, KeyboardInterrupt):
            print(f'YOLO node error: {exc}')
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
