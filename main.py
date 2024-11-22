import asyncio
import logging

import io


import requests
from PIL import Image
from PIL.ExifTags import TAGS
from aiogram.fsm.storage.memory import MemoryStorage

from config import *
import aiogram
from app.handlers import router, storage
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=storage)

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print('Exit')