# TG-Client-Search-Bot

A Telegram bot for automated searching and collecting repair/construction job orders from three Ukrainian marketplaces:

- 🐗 **Kabanchik.ua**
- 🏗 **Budver.ua**
- 🧱 **Rabotniki.ua**

The bot parses new tasks, filters duplicates, saves them into a PostgreSQL database and provides commands to search, export, clear and view statistics directly from Telegram.

---

## 🚀 Bot Commands (with screenshot markers)

### 🏁 `/start` — Welcome message  
Shows a short introduction and explains what the bot does.

**[SCREENSHOT_START_HERE]**

---

### ℹ️ `/help` — List of available commands  
Displays a full list of bot commands with descriptions.

**[SCREENSHOT_HELP_HERE]**

---

### 🔍 `/search [amount]` — Search for new job posts  
Runs all three parsers (Kabanchik, Budver, Rabotniki) and searches for new repair-related jobs in Kyiv.

- Argument `[amount]` is optional (default is `10`, minimum `1`, maximum `100`)
- Shows up to 2 newest tasks from each site directly in the chat
- Saves **all found orders** into the database
- Removes duplicates based on existing entries

Example:

```text
/search 15
```

**[SCREENSHOT_SEARCH_HERE]**

---

### 📊 `/export` — Export all saved orders to Excel  
Generates an `orders_export.xlsx` file with all saved orders and sends it to the user.

- After sending, the temporary file is deleted from the filesystem.

**[SCREENSHOT_EXPORT_HERE]**

---

### 🧹 `/clear_all` — Clear all order tables  
Drops all order tables used by the bot:

- `orders_kabanchik`
- `orders_budver`
- `orders_rabotniki`

Use this carefully — all stored data will be removed.

**[SCREENSHOT_CLEAR_ALL_HERE]**

---

### 📈 `/stats` — Database statistics  
Shows the current number of records in each table:

- Total orders from Kabanchik.ua
- Total orders from Budver
- Total orders from Rabotniki.ua
- Overall total number of saved orders

**[SCREENSHOT_STATS_HERE]**

---

## 📂 Project Structure

Approximate project structure:

```text
TG-Client-Search-Bot
│
├── bot.py                 # Main entry point, Telegram bot setup and run
├── config.py              # Configuration, environment variables, tokens, DB settings
├── database.py            # PostgreSQL connection and basic DB helpers
├── README.md              # Project documentation (this file)
├── requirements.txt       # Python dependencies
├── kabanchik_cookies.json # Optional cookies file for Kabanchik.ua
│
├── Keys/
│   └── data_keys.env      # Bot token, site credentials, DB credentials (not for commit)
│
├── handlers/
│   └── commands.py        # CommandHandlers class with all Telegram commands
│
├── parsers/
│   ├── budver_parser.py       # Parser for Budver.ua
│   ├── kabanchik_parser.py    # Parser for Kabanchik.ua
│   └── rabotniki_parser.py    # Parser for Rabotniki.ua
│
├── services/
│   └── order_service.py   # OrderService: fetching from all sites, exporting, DB access
│
└── for_test_parsers/
    ├── for_test_kabanchik.py  # Test script for Kabanchik parser/login
    └── test_rabotniki.py      # Test script for Rabotniki parser
```

---

## 🛠 Technologies

- **Python 3**
- **aiogram** — Telegram Bot API framework
- **Selenium** — for scraping job listings from websites
- **PostgreSQL** — for persistent storage of orders
- **openpyxl / pandas** (or similar) — for Excel export
- **asyncio** — asynchronous bot and parsing logic

---

## ⚙️ Configuration

Sensitive data (tokens, logins, passwords, DB config) should be stored in environment variables, for example in:

```text
Keys/data_keys.env
```

Example configuration:

```env
BOT_TOKEN=1234567890:ABCDEF...
ADMIN_ID=123456789
DATABASE_PUBLIC_URL=

KABANCHIK_LOGIN=email@gmail.com
KABANCHIK_PASSWORD=your_password
```

Make sure this file is not committed to the repository.

---

## 📦 Installation

1. **Clone the repository**

```bash
git clone https://github.com/6MrCrazy6/TG-Client-Search-Bot.git
cd TG-Client-Search-Bot
```

2. **Create and activate virtual environment**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the bot

After configuring your environment variables and installing dependencies, run:

```bash
python bot.py
```

The bot will start and connect to Telegram using your `BOT_TOKEN`.

---

## 🧪 Testing parsers separately

You can run and debug parsers without the bot using provided test scripts:

```bash
python for_test_parsers/for_test_kabanchik.py
python for_test_parsers/test_rabotniki.py
```

This is useful for checking authorization, cookies and HTML structure changes on the target websites.

---

## ✅ Summary

TG-Client-Search-Bot is a utility Telegram bot that helps to:

- Automatically search new repair/construction jobs from three different websites
- Avoid duplicates via database checks
- Export all collected orders to Excel
- Quickly view database statistics
- Clear all saved orders when needed