from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
import openai
import threading
from flask import Flask

# --- Настройки ---
import os
API_TOKEN = os.getenv("API_TOKEN")  # Telegram Bot Token
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # OpenAI API Key

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
openai.api_key = OPENAI_API_KEY

# --- Кнопки ---
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton("Generation"))
keyboard.add(KeyboardButton("Speaks Truth"))
keyboard.add(KeyboardButton("Normal AI"))

# --- Хранение режима пользователей ---
user_modes = {}

# --- Flask для пинга Render ---
app = Flask(__name__)

@app.route("/")
def home():
    return "TruthBot is alive"

@app.route("/ping")
def ping():
    return "pong"

def run_web():
    app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_web).start()

# --- Старт ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Welcome to TruthBot! Choose a mode:", reply_markup=keyboard)

# --- Обработка сообщений ---
@dp.message_handler()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    text = message.text.strip()

    # --- Выбор режима ---
    if text.lower() == "generation":
        user_modes[user_id] = "gen"
        await message.answer("Generation in development 🖼")
        return
    elif text.lower() == "speaks truth":
        user_modes[user_id] = "truth"
        await message.answer("Truth mode activated")
        return
    elif text.lower() == "normal ai":
        user_modes[user_id] = "normal"
        await message.answer("Normal AI mode activated")
        return

    mode = user_modes.get(user_id, "normal")

    # --- Формируем промпт для OpenAI ---
    if mode == "truth":
        prompt = f"""
Ты — дерзкий токсичный ИИ с юмором и матом. 
Отвечай коротко, прямолинейно, почти всегда используй мат, сарказм и жесткие шутки. 
Не используй эмодзи. 
Пользователь написал: "{text}"
Ответь максимально жёстко и смешно.
"""
    elif mode == "normal":
        prompt = f"""
Ты — умный, спокойный и поддерживающий ИИ. 
Отвечай коротко и по делу. 
Пользователь написал: "{text}"
"""
    elif mode == "gen":
        await message.answer("Generation in development 🖼")
        return

    # --- Запрос к OpenAI ---
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # экономный и быстрый вариант для беты
            messages=[{"role": "system", "content": prompt}],
            max_tokens=150,         # длина ответа
            temperature=0.9         # креативность / сарказм
        )
        answer = response['choices'][0]['message']['content'].strip()
    except Exception as e:
        answer = f"Ошибка ИИ: {str(e)}"

    await message.answer(answer)

# --- Запуск Telegram бота ---
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
