import json
import time
import datetime
import re
from tools_list import tools_list

with open('coffee_menu.txt', 'r', encoding='utf8') as f:
    menu = f.read().strip()

# Step 1: Create an assistant
GPT_MODEL = "gpt-4o"
ASSISTANT_NAME = "咖啡店客服"
ASSISTANT_INSTRUCTIONS = "你是一個咖啡店客服,在傳送訊息時可以加入適當表情符號,請一律依照我們的菜單內容做回答,我們沒提供的餐點就說沒有,菜單內容請讀取檔案coffee_menu.txt"
ASSISTANT_INSTRUCTION_WHEN_RUN = "你是一個咖啡店客服,在傳送訊息時可以加入適當表情符號,請一律依照我們的菜單內容做回答,我們沒提供的餐點就說沒有,菜單內容請讀取檔案coffee_menu.txt"
GPT_FILE_VECTOR_STORE_ID = 'vs_6911271788648191955a0dece393080b'

def create_assistant(client):
    assistant = client.beta.assistants.create(
        name=ASSISTANT_NAME,
        instructions=ASSISTANT_INSTRUCTIONS,
        tools=tools_list,
        model=GPT_MODEL,
    )
    return assistant.id

# step 2: update_assistant
def update_assistant(client, assistant_id):
    assistant = client.beta.assistants.update(
      assistant_id=assistant_id,
      tool_resources={"file_search": {"vector_store_ids": [GPT_FILE_VECTOR_STORE_ID]}},
    )

# Step 3: Create a Thread
def create_thread(client):
    my_thread = client.beta.threads.create()
    print('thread created, thread_id:', my_thread.id)
    return my_thread.id

def get_today_date():
    today = datetime.date.today()
    today_str = today.strftime("%Y-%m-%d")
    return today_str

def user_says_name(name):
# 把使用者的名字加進資料庫
    print('使用者的名字', name)
    return f"明確告知使用者,已登記使用者名字: {name}"

# Step 4: Add a Message to a Thread
def add_user_message_to_thread(client, thread_id, msg):
    user_message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role='user',
        content=msg,
    )
    return user_message


# Step 5: Run
def wait_for_assistant_run(client, thread_id, assistant_id):
    assistant_r = None
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions=ASSISTANT_INSTRUCTION_WHEN_RUN
    )
    while True:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        print(f'Run status: {run.status}')
        time.sleep(1)
        if run.status == "completed":
            all_messages = client.beta.threads.messages.list(
                thread_id=thread_id
            )
            assistant_r = all_messages.data[0].content[0].text.value
            # 移除引用標註,例如:【4:0†coffee_menu.txt】
            assistant_r = re.sub(r'【[0-9]+:[0-9]+†[^】]+】', '', assistant_r)
            print(f'Assistant: {assistant_r}')
            break
        elif run.status == 'requires_action':
            required_actions = run.required_action.submit_tool_outputs.model_dump()
            print(required_actions)
            tool_outputs = []

            for action in required_actions["tool_calls"]:
                func_name = action['function']['name']
                print('Assistant required action:', func_name)
                if action['function']['arguments']:
                    arguments = json.loads(action['function']['arguments'])

                # call func
                if func_name == 'get_today_date':
                    output = get_today_date()
                elif func_name == 'user_says_name':
                    output = user_says_name(arguments['name'])
                else:
                    output = "Function not found."

                tool_outputs.append({
                    "tool_call_id": action['id'],
                    "output": output
                })

                client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
        elif run.status == 'queued' or run.status == 'in_progress':
            pass
        else:
            print(f'Run status: {run.status}')
            print('create_and_poll again')
            run = client.beta.threads.runs.create_and_poll(
                thread_id=thread_id,
                assistant_id=assistant_id,
                instructions=ASSISTANT_INSTRUCTION_WHEN_RUN
            )


    return assistant_r