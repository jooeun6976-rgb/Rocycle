import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class TaskManagerNode(Node):
    def __init__(self):
        super().__init__('task_manager_node')

        self.state = 'IDLE'
        self.processed_count = 0

        self.voice_sub = self.create_subscription(
            String,
            '/voice_command',
            self.voice_command_callback,
            10,
        )

        self.state_pub = self.create_publisher(
            String,
            '/system_state',
            10,
        )

        self.conveyor_pub = self.create_publisher(
            String,
            '/conveyor_command',
            10,
        )

        self.get_logger().info('task_manager_node started')
        self.get_logger().info(f'현재 상태: {self.state}')
        self.publish_system_state()

    def publish_system_state(self):
        msg = String()
        msg.data = self.state
        self.state_pub.publish(msg)
        self.get_logger().info(f'/system_state 발행: {self.state}')

    def publish_conveyor_command(self, command):
        msg = String()
        msg.data = command
        self.conveyor_pub.publish(msg)
        self.get_logger().info(f'/conveyor_command 발행: {command}')

    def voice_command_callback(self, msg):
        command = msg.data.strip().upper()
        self.get_logger().info(f'음성 명령 수신: {command}')

        if command == 'START':
            if self.state in ('IDLE', 'STOPPED'):
                self.state = 'RUNNING'
                self.processed_count = 0
                self.publish_conveyor_command('START')
            else:
                self.get_logger().warning(
                    f'START 불가 - 현재 상태: {self.state}'
                )
                return

        elif command == 'PAUSE':
            if self.state == 'RUNNING':
                self.state = 'PAUSED'
                self.publish_conveyor_command('STOP')
            else:
                self.get_logger().warning(
                    f'PAUSE 불가 - 현재 상태: {self.state}'
                )
                return

        elif command == 'RESUME':
            if self.state == 'PAUSED':
                self.state = 'RUNNING'
                self.publish_conveyor_command('START')
            else:
                self.get_logger().warning(
                    f'RESUME 불가 - 현재 상태: {self.state}'
                )
                return

        elif command == 'STATUS':
            self.get_logger().info(
                f'현재 상태: {self.state}, 처리 개수: {self.processed_count}'
            )

        elif command == 'STOP':
            if self.state in ('RUNNING', 'PAUSED'):
                self.state = 'STOPPED'
                self.publish_conveyor_command('STOP')
            else:
                self.get_logger().warning(
                    f'STOP 불가 - 현재 상태: {self.state}'
                )
                return

        else:
            self.get_logger().warning(f'알 수 없는 명령: {command}')
            return

        self.publish_system_state()


def main(args=None):
    rclpy.init(args=args)
    node = TaskManagerNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
