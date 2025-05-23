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
HUGGINGFACE_TOKEN = os.getenv("HF_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"

headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Привет! Я онлайн-бот с бесплатным ИИ через HuggingFace.")

@dp.message()
async def chat(message: Message):
    payload = {"inputs": message.text}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(API_URL, headers=headers, json=payload) as resp:
                result = await resp.json()
                output = result[0]["generated_text"] if isinstance(result, list) else result.get("error", "Нет ответа.")
                await message.answer(output)
        except Exception as e:
            await message.answer(f"Ошибка: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
