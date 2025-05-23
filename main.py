import os
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = "https://openai.1rmb.tk/v1/chat/completions"

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
user_context = {}

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Я бесплатный AI-бот. Напиши любой вопрос.")

@dp.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    user_context.setdefault(user_id, [])
    user_context[user_id].append({"role": "user", "content": message.text})

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(API_URL, json={
                "model": "gpt-3.5-turbo",
                "messages": user_context[user_id]
            }) as resp:
                data = await resp.json()
                reply = data['choices'][0]['message']['content']
                user_context[user_id].append({"role": "assistant", "content": reply})
                await message.answer(reply)
        except Exception as e:
            await message.answer(f"Ошибка: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
