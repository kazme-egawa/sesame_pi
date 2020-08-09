import RPi.GPIO as GPIO
import time
import os
import sys
from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

# チャンネルシークレットとチャンネルアクセストークンの登録
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

# サーボモータを回す関数の登録
SERVO_PIN = 18
SERVO_OPEN_STATE = 7.0
SERVO_CLOSE_STATE = 2.5


def KeyOpener():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SERVO_PIN, GPIO.OUT)
    servo = GPIO.PWM(SERVO_PIN, 50)
    servo.start(0.0)
    servo.ChangeDutyCycle(SERVO_OPEN_STATE)
    time.sleep(1.0)
    GPIO.cleanup()


def KeyCloser():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SERVO_PIN, GPIO.OUT)
    servo = GPIO.PWM(SERVO_PIN, 50)
    servo.start(0.0)
    servo.ChangeDutyCycle(SERVO_CLOSE_STATE)
    time.sleep(1.0)
    GPIO.cleanup()


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    text = event.message.text

    # テキストの内容で条件分岐
    if text == 'ただいま':
        # 鍵開ける
        KeyOpener()
        # 返事
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage('おかえり〜　鍵開けといたよ')
        )
    elif text == '行ってきます':
        # 鍵閉める
        KeyCloser()
        # 返事
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage('いってらっしゃい　鍵閉めといたよ')
        )
    elif text == '開けて':
        # 鍵開ける
        KeyOpener()
        # 返事
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage('開けとくね')
        )
    elif text == '閉めて':
        # 鍵閉める
        KeyCloser()
        # 返事
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage('閉めとくね')
        )
    else:
        # 木霊
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text)
        )


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)
