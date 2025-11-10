tools_list = [
    {"type": "file_search"},
    {
        "type": "function",
        "function": {
            'name': 'get_today_date',
            'description': '如果使用者詢問日期,call this function,來取得日期',
        }
    },
    {
        "type": "function",
        "function": {
            'name': 'user_says_name',
            'description': '如果使用者提到名字,call this function',
            'parameters': {
                'type': 'object',
                'properties': {
                    'name': {
                        'type': 'string',
                        'description': '那個使用者的名字'
                    }
                },
                'required': ['name']
            }
        }
    },
]