import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import serial


class ConveyorNode(Node):
    def __init__(self):
        super().__init__('conveyor_node')

        self.port = '/dev/ttyACM0'
        self.baud = 9600
        self.on_speed = 100
        self.ser = None

        self.connect_conveyor()

        self.command_sub = self.create_subscription(
            String,
            '/conveyor_command',
            self.command_callback,
            10,
        )

        self.get_logger().info('conveyor_node started')
        self.get_logger().info('waiting for /conveyor_command')

    def connect_conveyor(self):
        try:
            self.ser = serial.Serial(
                self.port,
                self.baud,
                timeout=1,
            )
            self.get_logger().info(
                f'컨베이어 연결 성공: {self.port}'
            )

            # Arduino resets when the serial port is opened.
            time.sleep(2.2)
            self.ser.reset_input_buffer()

            # Safety stop at startup.
            self.send_speed(0)

        except serial.SerialException as exc:
            self.get_logger().error(
                f'컨베이어 연결 실패: {exc}'
            )
            self.ser = None

    def send_speed(self, speed):
        if self.ser is None or not self.ser.is_open:
            self.get_logger().error('컨베이어가 연결되어 있지 않습니다.')
            return

        command = f'{speed}\n'
        self.ser.write(command.encode('utf-8'))
        self.ser.flush()

        self.get_logger().info(
            f'컨베이어 속도 전송: {speed}'
        )

    def command_callback(self, msg):
        command = msg.data.strip().upper()
        self.get_logger().info(
            f'/conveyor_command 수신: {command}'
        )

        if command == 'START':
            self.send_speed(self.on_speed)

        elif command == 'STOP':
            self.send_speed(0)

        else:
            self.get_logger().warning(
                f'알 수 없는 컨베이어 명령: {command}'
            )

    def destroy_node(self):
        if self.ser is not None and self.ser.is_open:
            try:
                self.send_speed(0)
                self.ser.close()
            except serial.SerialException:
                pass

        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = ConveyorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
