import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, Update
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI, Request
import uvicorn

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "supersecret")

if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise ValueError("Токены Telegram и OpenAI должны быть установлены!")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
client = OpenAI(api_key=OPENAI_API_KEY)
app = FastAPI()
user_context = {}

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Я бот на базе ChatGPT. Напиши любой вопрос.")

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
        await message.answer(f"Ошибка: {e}")

@app.post(WEBHOOK_PATH)
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot=bot, update=update)
    return {"ok": True}

@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(f"{os.getenv('WEBHOOK_URL')}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
