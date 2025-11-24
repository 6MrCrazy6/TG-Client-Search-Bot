# TG Client Search Bot

A Telegram bot for automatically searching client tasks from Ukrainian repair-service platforms (Kabanchik, Budver, Rabotniki, etc.).  
The bot parses tasks via Selenium, filters duplicates, stores results in PostgreSQL, and provides export/statistics tools directly inside Telegram.

Built for repair teams, craftsmen, and service providers who need fast access to fresh client requests.

## Features

### /search — Find new tasks
The bot automatically logs in via Selenium, fetches tasks, removes duplicates, stores new records, and formats results.

### /stats — Database statistics
Shows number of tasks from each platform and total amount.

### /export — Export tasks to Excel
Generates `orders_export.xlsx` with all stored tasks.

### /help — Command list

## Core Functionality

- Task scraping from Kabanchik.ua, Budver, Rabotniki  
- Selenium dynamic parsing with authentication  
- Duplicate protection  
- PostgreSQL database  
- Formatted Telegram previews  
- Excel export  
- Fully async (Aiogram 3 + asyncpg)

## Project Structure

TG-Client-Search-Bot/
│── bot.py
│── config.py
│── requirements.txt
├── handlers/
├── parsers/
└── database/

## Technologies Used

Python 3.10+, Aiogram 3, Selenium, PostgreSQL, asyncpg, SQLAlchemy, openpyxl, dotenv

## How to Run

git clone https://github.com/6MrCrazy6/TG-Client-Search-Bot.git
cd TG-Client-Search-Bot
pip install -r requirements.txt

Create .env file, then:
python bot.py

## Future Improvements

- More platforms  
- Real-time notifications  
- Web analytics dashboard  
- ML task scoring  
- Docker container

## License
MIT
