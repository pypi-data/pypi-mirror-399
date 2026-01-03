import httpx
import json
import asyncio
import logging
import functools
from typing import List, Union, Callable, Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Rubio")

class Message:
    def __init__(self, bot, data: Dict[str, Any]):
        self.bot = bot
        self.raw = data
        self.type = data.get("type")
        self.chat_id = data.get("chat_id")
        
        msg = data.get("new_message", data.get("inline_message", {}))
        self.message_id = msg.get("message_id")
        self.sender_id = msg.get("sender_id")
        self.text = msg.get("text")
        self.aux_data = msg.get("aux_data", {})
        self.button_id = self.aux_data.get("button_id")

    async def reply(self, text: str, **kwargs):
        return await self.bot.send_message(self.chat_id, text, reply_to_message_id=self.message_id, **kwargs)

    async def delete(self):
        return await self.bot.delete_message(self.chat_id, self.message_id)

    async def edit(self, text: str):
        return await self.bot.edit_message_text(self.chat_id, self.message_id, text)

class Bot:
    def __init__(self, token: str):
        self.token = token
        self.api_url = f"https://botapi.rubika.ir/v3/{token}/"
        limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
        self.client = httpx.AsyncClient(
            base_url=self.api_url, 
            timeout=httpx.Timeout(10.0, connect=5.0),
            limits=limits,
            headers={"User-Agent": "Rubio/1.0.1 (No-Comments)"}
        )
        self.handlers = []
        self.callback_handlers = {}
        print("\n\x1b[38;5;196m[ Rubio Library ] \x1b[0mRunning on \x1b[1;37m@RubioLib\x1b[0m channel infrastructure.")

    def on_message(self, filters: Optional[Callable] = None, commands: Optional[List[str]] = None):
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(message: Message):
                if commands:
                    if not message.text: return
                    cmd_parts = message.text.split()
                    if not cmd_parts: return
                    cmd = cmd_parts[0].lower()
                    if cmd not in [f"/{c}" for c in commands]: return
                
                if filters and not filters(message): return
                return await func(self, message)
            self.handlers.append(wrapper)
            return wrapper
        return decorator

    def on_callback(self, button_id: Optional[str] = None):
        def decorator(func):
            if button_id:
                self.callback_handlers[button_id] = func
            else:
                self.callback_handlers["__all__"] = func
            return func
        return decorator

    async def _req(self, method: str, data: Optional[Dict] = None):
        try:
            response = await self.client.post(method, json=data or {})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"API Error [{method}]: {e}")
            return {"ok": False, "error": str(e)}

    async def get_me(self):
        return await self._req("getMe")

    async def send_message(self, chat_id: str, text: str, **kwargs):
        return await self._req("sendMessage", {"chat_id": chat_id, "text": text, **kwargs})

    async def delete_message(self, chat_id: str, message_id: str):
        return await self._req("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

    async def edit_message_text(self, chat_id: str, message_id: str, text: str):
        return await self._req("editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": text})

    async def run(self):
        logger.info("🚀 Rubio Engine Started | @RubioLib")
        offset_id = None
        while True:
            try:
                res = await self._req("getUpdates", {"limit": 50, "offset_id": offset_id})
                if res and res.get("updates"):
                    tasks = []
                    for up in res["updates"]:
                        msg = Message(self, up)
                        if msg.button_id:
                            handler = self.callback_handlers.get(msg.button_id) or self.callback_handlers.get("__all__")
                            if handler: tasks.append(asyncio.create_task(handler(self, msg)))
                        for h in self.handlers:
                            tasks.append(asyncio.create_task(h(msg)))
                    if tasks: await asyncio.gather(*tasks, return_exceptions=True)
                    offset_id = res.get("next_offset_id")
                await asyncio.sleep(0.05)
            except Exception as e:
                logger.error(f"Polling Error: {e}")
                await asyncio.sleep(2)

    async def __aenter__(self): return self
    async def __aexit__(self, *args): await self.client.aclose()
