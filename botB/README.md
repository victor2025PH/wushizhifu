# OTC Group Management Bot (Bot B)

Telegram Bot for managing OTC (Over-The-Counter) trading groups using python-telegram-bot (version 20+ async).

## Features

- ✅ Dual-bot mode support (reads Bot B token from second line of .env)
- ✅ SQLite database for storing admin settings
- ✅ OKX API integration for USDT/CNY price fetching
- ✅ Admin markup management
- ✅ USDT wallet address management

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create or update `.env` file in the parent directory (same level as `wushizhifu-otc-bot`):

```env
BOT_TOKEN=your_first_bot_token_here
BOT_TOKEN_B=your_second_bot_token_here
```

**Important**: Bot B will read the token from the second line of `.env` file, or from `BOT_TOKEN_B` environment variable.

### 3. Initialize Database

The database will be automatically initialized on first run. It will create:
- `otc_bot.db` - SQLite database file
- `settings` table with default values:
  - `admin_markup`: 0.0
  - `usdt_address`: (empty)

### 4. Run the Bot

```bash
python bot.py
```

## Database Schema

### settings Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| key | TEXT | Setting key (unique) |
| value | TEXT | Setting value |
| updated_at | TIMESTAMP | Last update time |

**Default Settings:**
- `admin_markup`: Floating point added to exchange rate (default: 0.0)
- `usdt_address`: USDT receiving wallet address (default: empty)

## API Integration

### OKX Public API

The bot uses OKX Public API to fetch USDT/CNY exchange rate:

- **Endpoint**: `https://www.okx.com/api/v5/market/ticker`
- **Method**: GET
- **Parameters**: `instId=USDT-CNY`
- **Response**: JSON with ticker data including `last` price

**Error Handling:**
- If OKX API fails, returns fallback price (default: 7.20 CNY)
- Logs all errors for debugging

## Commands

- `/start` - Start the bot and show welcome message
- `/help` - Display help information
- `/price` - Get current USDT/CNY price (with admin markup applied)
- `/settings` - View current settings (admin markup and USDT address)

## Project Structure

```
wushizhifu-otc-bot/
├── bot.py                 # Main bot entry point
├── config.py              # Configuration loader
├── database.py            # Database operations
├── requirements.txt      # Python dependencies
├── README.md             # This file
└── services/
    └── price_service.py  # OKX price fetching service
```

## Development Notes

### Dual-Bot Mode

This bot is designed to work alongside another bot (Bot A) in the same project. The configuration reads the second bot token from:
1. Second line of `.env` file (if it's just the token)
2. `BOT_TOKEN_B=...` format in `.env` file
3. `BOT_TOKEN_B` environment variable

### Price Fetching

The `get_okx_price()` function:
- ✅ Only called when requested (no background polling)
- ✅ Returns tuple: `(price: float or None, error_message: str or None)`
- ✅ Uses fallback price if OKX API fails
- ✅ Includes comprehensive error handling

### Database Operations

All database operations are handled through the `Database` class:
- `get_admin_markup()` - Get current markup value
- `set_admin_markup(markup)` - Update markup value
- `get_usdt_address()` - Get wallet address
- `set_usdt_address(address)` - Update wallet address

## License

Private project - All rights reserved

