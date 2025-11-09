import time

with open('coffee_menu.txt', 'r', encoding='utf8') as f:
    menu = f.read().strip()

# Step 1: Create an assistant
GPT_MODEL = "gpt-4o"
ASSISTANT_NAME = "咖啡店客服"
ASSISTANT_INSTRUCTIONS = "你是一個咖啡店客服,在傳送訊息時可以加入適當表情符號,請一律依照我們的菜單內容做回答,我們沒提供的餐點就說沒有,請使用繁體中文回答問題我們的菜單有:" + menu
ASSISTANT_INSTRUCTION_WHEN_RUN = "你是一個咖啡店客服,在傳送訊息時可以加入適當表情符號,請一律依照我們的菜單內容做回答,我們沒提供的餐點就說沒有,請使用繁體中文回答問題我們的菜單有:" + menu

def create_assistant(client):
    assistant = client.beta.assistants.create(
        name=ASSISTANT_NAME,
        instructions=ASSISTANT_INSTRUCTIONS,
        tools=[],
        model=GPT_MODEL,
    )
    return assistant.id

# Step 2: Create a Thread
def create_thread(client):
    my_thread = client.beta.threads.create()
    print('thread created, thread_id:', my_thread.id)
    return my_thread.id


# Step 3: Add a Message to a Thread
def add_user_message_to_thread(client, thread_id, msg):
    user_message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role='user',
        content=msg,
    )
    return user_message


# Step 4: Run
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
            print(f'Assistant: {assistant_r}')
            break
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