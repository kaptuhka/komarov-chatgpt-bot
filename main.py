import os
import openai
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

user_context = {}

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Привет! Я бот на базе ChatGPT. Задай мне любой вопрос.")

@dp.message_handler()
async def chat(message: types.Message):
    user_id = message.from_user.id
    user_context.setdefault(user_id, [])
    user_context[user_id].append({"role": "user", "content": message.text})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=user_context[user_id]
    )

    reply = response['choices'][0]['message']['content']
    user_context[user_id].append({"role": "assistant", "content": reply})
    await message.reply(reply)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
