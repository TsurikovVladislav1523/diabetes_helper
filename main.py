import os
import threading
import zipfile
from datetime import datetime
from flask import Flask, render_template, request, send_file
from flask import redirect, url_for
import random

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

import asyncio
import logging

import io


import requests
from PIL import Image
from PIL.ExifTags import TAGS
from aiogram.fsm.storage.memory import MemoryStorage
from statistic import *
from config import *
import aiogram
from app.handlers import router, storage, send_code
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=storage)

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

# Главная страница
@app.route("/patients/<int:tg_id>")
def patients(tg_id):
    # Пример данных о пациентах
    buttons = []
    users = get_obs_id(tg_id)
    for user in users:
        buttons.append({"id": user, "text": f"{user}"})
    print(buttons)
    return render_template("patients.html", buttons=buttons)


@app.route("/register", methods=["POST"])
def register():
    telegram_id = request.form["telegram_id"]
    try:
        # Генерация кода подтверждения
        verification_code = random.randint(1000, 9999)
        user_verification[telegram_id] = verification_code
        loop.create_task(send_code(verification_code, telegram_id))
        # Отправка кода через Telegram
        # bot.send_message(chat_id=telegram_id, text=f"Ваш код подтверждения: {verification_code}")
        return render_template("verify.html", telegram_id=telegram_id)
    except Exception as e:
        return f"Ошибка: {e}"

@app.route("/action/<int:button_id>", methods=["POST"])
def button_action(button_id):
    images = meal_stats_web(button_id)
    images.extend(sugar_level_web(button_id))
    user_data = get_user(button_id)
    # return render_template('final.html', images=images, user_data=user_data)
    return render_template('index1.html', images=images, user_data=user_data)

# Хранилище для проверки кода подтверждения
user_verification = {}

@app.route("/")
def home():
    return render_template("register1.html")


@app.route("/verify", methods=["POST"])
def verify():
    telegram_id = request.form["telegram_id"]
    entered_code = request.form["verification_code"]

    # Проверка кода
    if user_verification.get(telegram_id) == int(entered_code):
        return redirect(url_for(f"patients", tg_id=telegram_id))  # Перенаправление на страницу "Наблюдаемые пациенты"
    return "Неверный код подтверждения!"

def run_flask():
    app.run(host='0.0.0.0', port=8000, debug=False, use_reloader=False)

def create_zip(user_id):
    # Получаем текущую дату в формате YYYY-MM-DD
    current_date = datetime.now().strftime('%Y-%m-%d')

    # Формируем имя архива: "user_id_YYYY-MM-DD.zip"
    zip_filename = f"{user_id}_{current_date}.zip"
    zip_buffer = io.BytesIO()  # Буфер в памяти для ZIP-архива
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        # Считываем все файлы из папки uploads
        for image in os.listdir(UPLOAD_FOLDER):
            image_path = os.path.join(UPLOAD_FOLDER, image)
            if os.path.isfile(image_path):
                archive.write(image_path, os.path.basename(image_path))

    zip_buffer.seek(0)  # Возвращаем указатель в начало
    return zip_buffer, zip_filename

# Маршрут для скачивания архива с изображениями
@app.route('/download/<int:tg_id>"')
def download_zip(tg_id):
    zip_buffer, zip_filename = create_zip(tg_id)
    return send_file(zip_buffer, as_attachment=True, download_name=zip_filename, mimetype="application/zip")


if __name__ == "__main__":
    # Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    logging.basicConfig(level=logging.INFO)
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print('Exit')
