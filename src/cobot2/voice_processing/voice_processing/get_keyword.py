import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_srvs.srv import Trigger

from voice_processing.keyword_extraction import KeywordExtractor
from voice_processing.stt import STT
from voice_processing.wakeup_word import WakeupWord


class GetKeywordNode(Node):
    def __init__(self):
        super().__init__('get_keyword')

        self.service = self.create_service(
            Trigger,
            '/get_keyword',
            self.get_keyword_callback,
        )

        self.voice_pub = self.create_publisher(
            String,
            '/voice_command',
            10,
        )

        self.wakeup_word = WakeupWord()
        self.stt = STT()
        self.keyword_extractor = KeywordExtractor()

        self.get_logger().info('get_keyword node started')
        self.get_logger().info('Publisher ready: /voice_command')

    def get_keyword_callback(self, request, response):
        del request

        try:
            detected = self.wakeup_word.detect(timeout=30)

            if not detected:
                response.success = False
                response.message = '호출어 감지 실패'
                return response

            sentence = self.stt.listen()

            if not sentence:
                response.success = False
                response.message = '음성 인식 실패'
                return response

            self.get_logger().info(
                f'STT 인식 결과: {sentence}'
            )

            command = self.keyword_extractor.extract_keyword(sentence)

            self.get_logger().info(
                f'명령 분류 결과: {command}'
            )

            if command == 'UNKNOWN':
                response.success = False
                response.message = '명령을 이해하지 못했습니다.'
                return response

            msg = String()
            msg.data = command
            self.voice_pub.publish(msg)

            self.get_logger().info(
                f'/voice_command 발행: {command}'
            )

            response.success = True
            response.message = command
            return response

        except Exception as exc:
            self.get_logger().error(f'음성 처리 오류: {exc}')
            response.success = False
            response.message = '음성 처리 중 오류가 발생했습니다.'
            return response


def main(args=None):
    rclpy.init(args=args)
    node = GetKeywordNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
