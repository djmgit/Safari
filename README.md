## Setting up

- Run ``` sudo pip install -r requirements.txt```
- Setup Postgresql
- Run ``` python manage.py db init```
- Run ``` python manage.py migrate```
- Run ``` python main.py```

## Dependencies

- python3
- AIML
- python-aiml
- Flask
- Flask-admin
- SqlAlchemy
- Postgresql

## Files

**bot_core** - bot library

- bot/bot.py - chatbot, returns answer in json (type, action, param) to be processed by flask server
- bot/rules.aiml - bot grammar **(needs to be enhanced for smooth conversation)**
- bot/std-startup.xml - entry point of bot

**API server**

- main.py - api server. It will interact with the bot to get reply and will then generate result with 
            required information

- manage.py - Applies migrations

## Workflow

- User provides input (for example: tell me something about purulia)
- Input is forwared to server
- Server passes the input to bot
- Bot parses and returns response : {'type': 'action', 'action': 'info', param: 'purulia'}
- Flask reads the response, extracts required information, in this case info on purulia
- Flask generates response and serves it in form of json

## Endpoints

- ```http://127.0.0.1:5000/api/chat?q=[user_input]```

- For example: ```http://127.0.0.1:5000/api/chat?q=tell%20me%20something%20about%20purulia```

**Admin for adding data**

- ```http://127.0.0.1:5000/admin/```
