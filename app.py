import os
import json
from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

app = Flask(__name__)

from openai import OpenAI
from gpt_funcs import create_assistant, create_thread, add_user_message_to_thread, wait_for_assistant_run, update_assistant

# Read configuration from key.json or environment variables
def load_config():
    config = {}
    try:
        with open('key.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        pass

    # Get values from config file or environment variables
    openai_api_key = config.get('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY')
    line_access_token = config.get('LINE_ACCESS_TOKEN') or os.getenv('LINE_ACCESS_TOKEN')
    webhook_secret = config.get('WEBHOOK_SECRET') or os.getenv('WEBHOOK_SECRET')

    return openai_api_key, line_access_token, webhook_secret

api_key, token, webhook_secret = load_config()

handler = WebhookHandler(webhook_secret)
configuration = Configuration(access_token=token)
client = OpenAI(api_key=api_key)


assistant_id = create_assistant(client)
update_assistant(client, assistant_id)
tread_id = create_thread(client)
# tread_id = 'thread_KH5l8sKKXwpngqeE5KWj1vYP'  # Use a fixed thread ID for simplicity

@app.route("/", methods=['POST'])

def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_msg = event.message.text
    add_user_message_to_thread(client, tread_id, user_msg)
    assistant_r = wait_for_assistant_run(client, tread_id, assistant_id)

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        r = ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=assistant_r)]
            )
        line_bot_api.reply_message_with_http_info(r)

if __name__ == "__main__":
    app.run()

