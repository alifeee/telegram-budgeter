# Telegram Budgeter

This is a project to run on a server or Raspberry Pi which sends me a Telegram message every day asking how much I spent the day before. The idea is to keep track of average daily spending.

![Chat with "Bank Bot": "How much did you spend yesterday?" - "12.98" - "New average: 19.45"](images/conversation.png)

## Requirements

For Google Sheets integration, many python modules are available ([gspread], [gsheets], [pygsheets], [EZSheets]). I use [gspread] as it seems up-to-date, and has a good range of [examples](https://docs.gspread.org/en/latest/user-guide.html).

| Requirement | Version |
| ----------- | ------- |
| Python      | 3.11.1  |

[gspread]: https://pypi.org/project/gspread/
[gsheets]: https://pypi.org/project/gsheets/
[pygsheets]: https://pypi.org/project/pygsheets/
[EZSheets]: https://pypi.org/project/EZSheets/

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
python ./bot.py
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

### Set up environment on server

```bash
ssh root@...
cd ~/python
git clone https://github.com/alifeee/telegram-budgeter.git
cd telegram-budgeter
sudo apt-get update
sudo apt install python3.10-venv
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

### Move over secrets

```bash
scp google_credentials.json root@...:~/python/telegram-budgeter/
scp .env root@...:~/python/telegram-budgeter/
```

### Run bot

```bash
ssh root@...
tmux
cd ~/python/telegram-budgeter
source env/bin/activate
python ./bot.py
# Ctrl+B, D to detach from tmux
```

### List tmux sessions

```bash
tmux ls
```

### Attach to tmux session

```bash
tmux attach -t 0
```

### Kill tmux session

```bash
tmux kill-session -t 0
```

### Update

```bash
ssh root@...
cd ~/python/telegram-budgeter
git pull
```

Then repeat steps in [Run](#run-bot)
