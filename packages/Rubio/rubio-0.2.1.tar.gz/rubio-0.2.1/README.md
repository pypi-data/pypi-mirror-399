# Rubio 🚀 (v0.2.0)
### The Ultimate Rubika Bot Framework

Powered by `httpx` for extreme speed and efficiency. Developed by **@RubioLib**.

## Features
- **FastHTTP Integration**: Uses `httpx` for high-performance async requests.
- **Ultra-Simple API**: Inspired by the best, optimized for humans.
- **Official Channel**: Join us at **@RubioLib** for updates.

## Installation
```bash
pip install Rubio --upgrade
```

## Quick Start
```python
import asyncio
from rubio import Bot

async def main():
    async with Bot("YOUR_TOKEN") as bot:
        # Simple and powerful
        await bot.send_message("CHAT_ID", "Hello from the new Rubio!")
        
        # Get bot info
        me = await bot.get_me()
        print(f"I am {me['bot']['bot_title']}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Methods
- `send_message(chat_id, text, **kwargs)`
- `get_me()`
- `get_updates(limit=10, offset_id=None)`
- `delete_message(chat_id, message_id)`

Join **@RubioLib** to crush the competition.
