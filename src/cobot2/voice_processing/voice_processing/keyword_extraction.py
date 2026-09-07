from openai import OpenAI


ALLOWED_COMMANDS = {
    'START',
    'PAUSE',
    'RESUME',
    'STATUS',
    'STOP',
    'UNKNOWN',
}


class KeywordExtractor:
    def __init__(self):
        # API key is intentionally not stored in this repository.
        # Configure OpenAI authentication only in the local runtime environment.
        self.client = OpenAI()

    def extract_keyword(self, sentence):
        if not sentence:
            return 'UNKNOWN'

        prompt = f"""
다음 사용자의 음성 명령을 아래 명령 중 정확히 하나로 분류하세요.

START
PAUSE
RESUME
STATUS
STOP
UNKNOWN

분류 규칙:

START
- 분리수거 시작해줘
- 작업 시작해줘
- 분리수거 시작
- 작업 시작

PAUSE
- 잠깐 멈춰
- 잠시 멈춰
- 일시정지해줘
- 잠깐만 멈춰

RESUME
- 다시 시작해
- 다시 시작해줘
- 계속해
- 작업 재개해줘
- 다시 진행해줘

STATUS
- 지금까지 몇 개 처리했어?
- 몇 개 처리했어?
- 처리 현황 알려줘
- 지금까지 처리한 개수 알려줘

STOP
- 그만하자
- 작업 종료해줘
- 분리수거 종료해줘
- 이제 그만
- 작업 끝내줘

주의:
PAUSE는 일시정지입니다.
STOP은 작업 종료입니다.
START는 최초 작업 시작입니다.
RESUME은 일시정지된 작업을 다시 시작하는 명령입니다.

반드시 명령어 하나만 출력하세요.

사용자 입력:
{sentence}
"""

        response = self.client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {
                    'role': 'user',
                    'content': prompt,
                }
            ],
            temperature=0,
        )

        command = response.choices[0].message.content.strip()

        if command not in ALLOWED_COMMANDS:
            return 'UNKNOWN'

        return command
