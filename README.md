
This repository contains a lightweight Telegram bot that *automatically approves chat join requests* for groups where it is an admin. All visible text will be shown in a small-caps-like Unicode style.

## Files
- `main.py` — main bot code (auto-accept logic, small-caps messages)
- `requirements.txt` — dependencies
- `Procfile` — for Render deployment
- `.env.example` — example environment variable

## Quick Setup for Render
1. Create a new Web Service on Render. Use this repository.
2. Set the environment variable `BOT_TOKEN` to your BotFather token.
3. Make the bot an administrator in the groups where you want it to auto-approve requests.
4. Deploy; Render will run `python main.py` as configured in the Procfile.

## Important Notes
- The bot uses long-polling (suitable for Render web/worker services).
- Private messages to users may fail due to Telegram privacy settings — those failures are caught and logged.

---# POWERFUL-REQUEST-ACCEPT
