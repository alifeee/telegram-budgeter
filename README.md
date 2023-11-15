# Telegram Budgeter

This is a project to run on a server which sends me a Telegram message every day asking how much I spent the day before. The idea is to keep track of average daily spending.

![Chat with "Bank Bot": "How much did you spend yesterday?" - "12.98" - "New average: 19.45"](images/conversation.png)

## Requirements

| Requirement | Version |
| ----------- | ------- |
| Python      | 3.11.1  |
| Google Sheets | - |

## Commands

### Set up environment

```bash
python3 -m venv env
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Test

```bash
pytest
ptw # Run with watch
```

### Run

```bash
python3 ./bot.py
```

## Google Credentials

Credentials are stored in `google_credentials.json`. Follow the [gspread "Service Account" guide][gspread-guide] to set up a service account and download the credentials JSON file.

```json
{
  "type": "service_account",
  "project_id": "telegram-budgeter",
  "private_key_id": "[PRIVATE KEY ID]",
  "private_key": "[PRIVATE KEY]",
  "client_email": "...@....gserviceaccount.com",
  "client_id": "[CLIENT ID]",
  ...
}
```

[gspread-guide]: https://docs.gspread.org/en/latest/oauth2.html#for-bots-using-service-account

## Telegram

### Credentials

To obtain an access token for telegram, see [help page](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Introduction-to-the-API), but in essence, talk to the [BotFather](https://t.me/botfather).

The access token is used via an environment variable, or a `.env` file, which is not tracked by git.

Also in the environment should be an "admin ID", where errors are sent via the error handler.

```bash
touch .env
```

```.env
TELEGRAM_BOT_ACCESS_TOKEN=...
ADMIN_USER_ID=...
```

### Change commands

To change the commands, talk to the [BotFather](https://t.me/botfather) and use the `/setcommands` command.

```text
/setcommands
...
stats - Get spending statistics
spreadsheet - Get spreadsheet URL
spend - Set a day's spend
remind - Set reminders on/off
start - Set spreadsheet/restart
help - See help
privacy - See privacy information
cancel - cancel the current operation
```

## Persistent data

To store each user's Google Sheet ID, a persistent pickle file is used. This is not tracked by git. This uses the [Persistence API](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Making-your-bot-persistent) from [python-telegram-bot][ptb].

[ptb]: https://github.com/python-telegram-bot/python-telegram-bot/

```python
persistent_data = PicklePersistence(filepath="bot_data.pickle")
application = Application.builder().token(API_KEY).persistence(persistent_data).build()
```

## Deploy on remote server

### Initial deployment

```bash
ssh $USER@$SERVER
cd ~/python
git clone https://github.com/alifeee/telegram-budgeter.git
cd telegram-budgeter
sudo apt-get update
sudo apt install python3.10-venv
tmux new -s telegram_budgeter
cd ~/python/telegram-budgeter
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python3 ./bot.py
# Ctrl+B, D to detach from tmux
```

#### Move over secrets

```bash
scp google_credentials.json $USER@$SERVER:~/python/telegram-budgeter/
scp .env $USER@$SERVER:~/python/telegram-budgeter/
```

### Update deployment

```bash
ssh $USER@$SERVER
tmux ls
tmux attach -t telegram_budgeter
# send ctrl+C
git pull
python3 ./bot.py
# Ctrl+B, D to detach from tmux
```
