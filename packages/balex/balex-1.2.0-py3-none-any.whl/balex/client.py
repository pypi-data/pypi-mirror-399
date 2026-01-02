import asyncio
import aiohttp

class BotClient:
    BASE_URL = "https://tapi.bale.ai/bot"

    def __init__(self, token: str):
        self.token = token
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()


    async def _ensure_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()

    def _run(self, coro):
        try:
            loop = asyncio.get_running_loop()
            return coro 
        except RuntimeError:
            return asyncio.run(coro)

    async def _post(self, method: str, data: dict):
        await self._ensure_session()
        url = f"{self.BASE_URL}{self.token}/{method}"
        async with self.session.post(url, json=data) as resp:
            return await resp.json()

    def send_message(self, chat_id: int, text: str):
        return self._run(self._send_message(chat_id, text))

    async def _send_message(self, chat_id: int, text: str):
        return await self._post("sendMessage", {
            "chat_id": chat_id,
            "text": text
        })

    def set_webhook(self, url: str):
        return self._run(self._set_webhook(url))

    async def _set_webhook(self, url: str):
        return await self._post("setWebhook", {"url": url})

