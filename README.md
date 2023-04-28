# Telegram Budgeter

This is a project to run on a server or raspberry pi which sends me a Telegram message every day asking how much I spent the day before. The idea is to keep track of average daily spending.

![Chat with "BankBot": "How much did you spend yesterday?" - "12.98" - "New average: 19.45"](images/conversation.png)

## Requirements

For Google Sheets integration, many python modules are available ([gspread], [gsheets], [pygsheets], [EZSheets]). I use [gspread] as it seems up to date, and has a good range of [examples](https://docs.gspread.org/en/latest/user-guide.html).

| Requirement | Version |
| ----------- | ------- |
| Python      | 3.11.1  |

[gspread]: https://pypi.org/project/gspread/
[gsheets]: https://pypi.org/project/gsheets/
[pygsheets]: https://pypi.org/project/pygsheets/
[EZSheets]: https://pypi.org/project/EZSheets/
