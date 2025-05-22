import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv
from openai import OpenAI

# Загрузка переменных из .env (для локального запуска)
load_dotenv()

# Получение API ключей
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Проверка, что переменные окружения не пустые
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment.")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in environment.")

# Инициализация OpenAI и Telegram
client = OpenAI(api_key=OPENAI_API_KEY)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Контекст по каждому пользователю
user_context = {}

@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Привет! Я бот на базе ChatGPT. Напиши мне любой вопрос.")

@dp.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    user_context.setdefault(user_id, [])
    user_context[user_id].append({"role": "user", "content": message.text})

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=user_context[user_id]
        )
        reply = response.choices[0].message.content
        user_context[user_id].append({"role": "assistant", "content": reply})
        await message.answer(reply)
    except Exception as e:
        await message.answer(f"Ошибка при обращении к OpenAI: {e}")

async def main():
    await dp.start_webhook(bot)

if __name__ == "__main__":
    asyncio.run(main())
