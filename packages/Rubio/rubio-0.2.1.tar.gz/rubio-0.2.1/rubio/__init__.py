import httpx
import json
import asyncio

class Bot:
    def __init__(self, token):
        self.token = token
        self.api_url = f"https://botapi.rubika.ir/v3/{token}/"
        self.client = httpx.AsyncClient(base_url=self.api_url, timeout=30.0)
        print("\n\x1b[38;5;196m[ Rubio Library ] \x1b[0mRunning on \x1b[1;37m@RubioLib\x1b[0m channel infrastructure.")

    async def _req(self, method, data=None):
        response = await self.client.post(method, json=data or {})
        return response.json()

    async def get_me(self):
        return await self._req("getMe")

    async def send_message(self, chat_id, text, **kwargs):
        data = {"chat_id": chat_id, "text": text, **kwargs}
        return await self._req("sendMessage", data)

    async def send_poll(self, chat_id, question, options):
        return await self._req("sendPoll", {"chat_id": chat_id, "question": question, "options": options})

    async def get_updates(self, limit=10, offset_id=None):
        data = {"limit": limit}
        if offset_id: data["offset_id"] = offset_id
        return await self._req("getUpdates", data)

    async def delete_message(self, chat_id, message_id):
        return await self._req("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
