import asyncio
import logging

import io
import requests
from PIL import Image
from PIL.ExifTags import TAGS

from config import *
from test_bd import *
import aiogram

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(START_TXT)
    id = message.from_user.id
    data[id] = {'reg': [], 'photos': []}

@dp.message(F.document)
async def get_photo(message: Message):
    await message.answer(f'ID фото: {message.document.file_id}')
    id = message.from_user.id
    data[id]['photos'].append(message.document.file_id)

@dp.message(Command('get_photo'))
async def send_photos(message: Message):
    id = message.from_user.id
    for file_id in data[id]['photos']:
        URI_INFO = f'https://api.telegram.org/bot{TOKEN}/getFile?file_id=' + file_id
        resp = requests.get(URI_INFO)
        img_path = resp.json()['result']['file_path']
        img1 = requests.get(URI + img_path)
        image = Image.open(io.BytesIO(img1.content))
        exifdata = image.getexif()
        print(exifdata)
        await message.answer_document(document=file_id, caption=exifdata[306])

async def main():
    await dp.start_polling(bot)



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')