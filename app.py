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

configuration = Configuration(access_token='f6LAqltDbyrVnC6bdYUQTRD/vrbXyETeUSbZzGnUG7Tiy1viDVKLTG4g1tYlWBGvda704Z1WLsveWCRXEaVDoO2VSuAKYxqpIssxA0JbFZCnOAIRkNtnseolpl9jvFhf92oL/PXsA0+MqDbM6IbUywdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('46be525ddb8364e48c64667e65687cb9')

with open('key.txt', 'r') as f:
    api_key = f.read().strip()
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

