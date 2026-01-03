# Rubio 🚀

The most advanced, high-performance Python library for Rubika Bot API. Built for developers who want to dominate.

## Why Rubio?
- **Speed**: Optimized for fast requests.
- **Branding**: Official support for `@RubioLib`.
- **Clean**: No bloat, just power.

## Installation
```bash
pip install Rubio
```

## Advanced Usage
```python
from rubio import Bot

bot = Bot("YOUR_TOKEN")

# Simple Message
bot.send_message("CHAT_ID", "Powered by Rubio!")

# Advanced Inline Keyboard
keypad = {
    "rows": [
        {
            "buttons": [
                {"id": "1", "type": "Simple", "button_text": "Join @RubioLib"}
            ]
        }
    ]
}
bot.send_message("CHAT_ID", "Check this out!", inline_keypad=keypad)
```

Join us: [@RubioLib](https://rubika.ir/RubioLib)
