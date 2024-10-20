import asyncio
import logging

import io
import requests
from PIL import Image
from PIL.ExifTags import TAGS

from data_base import *
from config import *
import app.keyboards as kb


from app.sheduler import *
import datetime as dt
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

bot = Bot(token=TOKEN)
router = Router()
sheduler = AsyncIOScheduler(timezone="Europe/Moscow")
sheduler.start()


#sheduler.add_job(send_message_time, trigger="date", run_date=dt.datetime.now() + dt.timedelta(seconds=1), kwargs={'bot': bot})
#sheduler.add_job(send_message_cron, trigger="cron", hour=dt.datetime.now().hour, minute=dt.datetime.now().minute + 1,
#                 start_date=dt.datetime.now(), kwargs={'bot': bot})
#sheduler.add_job(send_message_interval, trigger="interval",seconds=3, kwargs={'bot': bot})

registered = get_all_users()
print(registered)

for tg_id, time in get_times_with_tg_id():
    hours, minutes = map(int, time.split(":"))
    # print(tg_id, minutes, hours)
    sheduler.add_job(send_message_cron, trigger="cron", hour=hours,
                     minute=minutes,
                     start_date=dt.datetime.now(), kwargs={'bot': bot, "chat_id": tg_id})


class Reg(StatesGroup):
    gender = State()
    height = State()
    weight = State()
    age = State()
    meals = State()



@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(START_TXT)
    if message.from_user.id not in registered:
        await message.answer(
            "Вы не зарегистрированы в системе. Пожалуйста введите комаду /reg для прохождения регистрации")


@router.message(F.document)
async def get_photo(message: Message):
    # await message.answer(f'ID фото: {message.document.file_id}')
    id = message.from_user.id
    if id in registered:
        file_id = message.document.file_id
        URI_INFO = f'https://api.telegram.org/bot{TOKEN}/getFile?file_id=' + file_id
        resp = requests.get(URI_INFO)
        img_path = resp.json()['result']['file_path']
        img1 = requests.get(URI + img_path)
        image = Image.open(io.BytesIO(img1.content))
        exifdata = image.getexif()
        # t_n = dt.datetime(exifdata[306].split(":"))
        t_d = dt.datetime.now() - dt.datetime.strptime(exifdata[306], '%Y:%m:%d %H:%M:%S')
        delta = t_d.seconds / 60
        if delta > 10:
            await message.answer(
                "Данное фото было сделано заранее, пожалуйста, отправьте актуальные данные")
        # создать задачу-напоминание
        else:
            await message.answer(
                "Данные успешно сохранены")
    else:
        await message.answer(
            "Вы не зарегистрированы в системе. Пожалуйста введите комаду /reg для прохождения регистрации")

@router.message(F.photo)
async def get_photo(message: Message):
    await message.answer(f'Отправьте, пожалуйста, данное фото без сжатия')


# @router.message(Command('get_photo'))
# async def send_photos(message: Message):
#     id = message.from_user.id
#     for file_id in data[id]['photos']:
#         URI_INFO = f'https://api.telegram.org/bot{TOKEN}/getFile?file_id=' + file_id
#         resp = requests.get(URI_INFO)
#         img_path = resp.json()['result']['file_path']
#         img1 = requests.get(URI + img_path)
#         image = Image.open(io.BytesIO(img1.content))
#         exifdata = image.getexif()
#         print(exifdata)
#
#         await message.answer_document(document=file_id, caption=exifdata[306])
#
#     await message.answer("Вы не зарегистрированы в системе. Пожалуйста введите комаду /reg для прохождения регистрации")


@router.message(Command('reg'))
async def reg_one(message: Message, state: FSMContext):
    await state.set_state(Reg.gender)
    await message.answer_photo(photo=logo, caption="Введите Bаш пол", reply_markup=kb.gender_key)


@router.callback_query(F.data == 'man', Reg.gender)
async def reg_two(callback: CallbackQuery, state: FSMContext):
    text = "male"
    await state.update_data(gender=text)
    await state.set_state(Reg.height)
    await callback.message.delete_reply_markup()
    await callback.message.edit_caption(caption="Введите Ваш рост")


@router.callback_query(F.data == 'women', Reg.gender)
async def reg_two(callback: CallbackQuery, state: FSMContext):
    text = "wom"
    await state.update_data(gender=text)
    await state.set_state(Reg.height)
    await callback.message.edit_caption(caption='Введите Ваш рост')


@router.message(Reg.height)
async def reg_three(message: Message, state: FSMContext):
    await state.update_data(height=message.text)
    await state.set_state(Reg.weight)
    await message.answer_photo(photo=logo, caption="Введите Bаш вес")
    # await message.edit_caption(caption='Введите Ваш вес')


@router.message(Reg.weight)
async def reg_four(message: Message, state: FSMContext):
    await state.update_data(weight=message.text)
    await state.set_state(Reg.age)
    await message.answer_photo(photo=logo, caption="Введите Bаш возраст")
    # await message.edit_caption(caption='Введите Ваш возраст')


@router.message(Reg.age)
async def reg_five(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await state.set_state(Reg.meals)
    await message.answer_photo(photo=logo, caption="Введите время Ваших приемов пищи через пробел в формате: {ЧЧ:ММ}")


@router.message(Reg.meals)
async def reg_five(message: Message, state: FSMContext):
    await state.update_data(meals=message.text.split(" "))
    id = message.from_user.id
    date_state = await state.get_data()
    print(date_state)
    create_user(id, date_state["gender"], date_state["height"], date_state["weight"],
                date_state["age"])
    for time in date_state["meals"]:
        add_time(id, time)
        hours, minutes = map(int, time.split(":"))
        # print(tg_id, minutes, hours)
        sheduler.add_job(send_message_cron, trigger="cron", hour=hours,
                         minute=minutes,
                         start_date=dt.datetime.now(), kwargs={'bot': bot, "chat_id": id})
    registered.append(id)
    await message.answer('Спасибо, регистрация завершена.')
    await state.clear()


@router.message(Command("reg_data"))
async def reg_data(message: Message):
    id = message.from_user.id
    print(get_user(id))
    print(get_times(id))
