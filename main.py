import os
import openai
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv

load_dotenv()

# Получаем токены из переменных окружения
openai.api_key = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Инициализация бота и диспетчера
bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher(storage=MemoryStorage())

# Словарь для хранения контекста по каждому пользователю
user_context = {}

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Привет! Я бот на базе ChatGPT. Задай мне любой вопрос.")

@dp.message()
async def chat(message: Message):
    user_id = message.from_user.id
    user_context.setdefault(user_id, [])
    user_context[user_id].append({"role": "user", "content": message.text})

    try:
       from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=user_context[user_id]
)
reply = response.choices[0].message.content

        )
        reply = response['choices'][0]['message']['content']
        user_context[user_id].append({"role": "assistant", "content": reply})
        await message.answer(reply)
    except Exception as e:
        await message.answer(f"Ошибка: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
