from openai import OpenAI

# 读取API key
with open('key.txt', 'r') as f:
    api_key = f.read().strip()

client = OpenAI(api_key=api_key)
completion = client.chat.completions.create(
    model="gpt-5",
    messages=[
        {"role": "system", "content": "你是一個line聊天機器人."},
        {"role": "user", "content": "你好嗎?"}
    ]
)

gpt_reply = completion.choices[0].message.content
print(gpt_reply)