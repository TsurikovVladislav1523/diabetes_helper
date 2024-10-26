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

# sheduler.add_job(send_message_time, trigger="date", run_date=dt.datetime.now() + dt.timedelta(seconds=1), kwargs={'bot': bot})
# sheduler.add_job(send_message_cron, trigger="cron", hour=dt.datetime.now().hour, minute=dt.datetime.now().minute + 1,
#                 start_date=dt.datetime.now(), kwargs={'bot': bot})
# sheduler.add_job(send_message_interval, trigger="interval",seconds=3, kwargs={'bot': bot})

registered = get_all_users()
print(registered)

for tg_id, time, name in get_times_with_tg_id():
    hours, minutes = map(int, time.split(":"))
    # print(tg_id, minutes, hours)
    sheduler.add_job(send_message_cron, trigger="cron", hour=hours,
                     minute=minutes,
                     start_date=dt.datetime.now(), kwargs={'bot': bot, "chat_id": tg_id, "name": name})


class Reg(StatesGroup):
    gender = State()
    height = State()
    weight = State()
    age = State()
    meals = State()
    msg_id = State()


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
            add_measurement(id, file_id) # !!! Вот тут дописать уровень сахара 3м параметром
            await message.answer(
                f"Данные успешно сохранены, ID фото: {message.document.file_id}, Время: {t_d}, Время фото: {exifdata[306]}")
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

class Change(StatesGroup):
    height = State()
    weight = State()
    age = State()
    meals = State()
    msg_id = State()


@router.message(Command('change_par'))
async def change_p_one(message: Message, state: FSMContext):
    msg = await message.answer_photo(photo=logo, caption="Выберете параметр, который хотите изменить",
                                     reply_markup=kb.change_key)


@router.callback_query(F.data == 'height')
async def change_two(callback: CallbackQuery, state: FSMContext):
    id = callback.from_user.id
    params = get_user(id)
    msg = await callback.message.answer(
        f"Ваш текущий рост: {params[3]}. Если хотите его изменить, ввидите новое значение. Если хотите оставить текущее значение, введите НЕТ")
    await state.set_state(Change.height)


@router.message(Change.height)
async def reg_three(message: Message, state: FSMContext):
    txt = message.text
    id = message.from_user.id
    params = get_user(id)
    await state.clear()
    if txt != "НЕТ":
        update_user_h(id, txt)


@router.callback_query(F.data == 'weight')
async def change_two(callback: CallbackQuery, state: FSMContext):
    id = callback.from_user.id
    params = get_user(id)
    msg = await callback.message.answer(
        f"Ваш текущий вес: {params[4]}. Если хотите его изменить, ввидите новое значение. Если хотите оставить текущее значение, введите НЕТ")
    await state.set_state(Change.weight)


@router.message(Change.weight)
async def reg_three(message: Message, state: FSMContext):
    txt = message.text
    id = message.from_user.id
    params = get_user(id)
    await state.clear()
    if txt != "НЕТ":
        update_user_w(id, txt)


class Menu(StatesGroup):
    drinks = State()
    salats = State()
    soups = State()
    main = State()


@router.message(Command('create_menu'))
async def menu(message: Message, state: FSMContext):
    await message.answer(
        f"Для составления Вашего рациона введите введите название приема пищи, указанное при регистрации")
    await state.set_state(Menu.drinks)


@router.message(Menu.drinks)
async def reg_three(message: Message, state: FSMContext):
    await message.answer(
        f"Введите напитки, которые вы пьете в этот прием пиши в формате \n Напиток1 [пробел дефис пробел] Кол-во ХЕ \n Напиток2 [пробел дефис пробел] Кол-во ХЕ")
    await state.set_state(Menu.salats)


@router.message(Menu.salats)
async def reg_three(message: Message, state: FSMContext):
    await message.answer(
        f"Введите салаты, которые вы едите в этот прием пиши в формате \n Салат1 [пробел дефис пробел] Кол-во ХЕ \n Салат2 [пробел дефис пробел] Кол-во ХЕ")
    await state.set_state(Menu.soups)


@router.message(Menu.soups)
async def reg_three(message: Message, state: FSMContext):
    await message.answer(
        f"Введите супы или каши, которые вы едите в этот прием пиши в формате \n Суп1 [пробел дефис пробел] Кол-во ХЕ \n Каша2 [пробел дефис пробел] Кол-во ХЕ")
    await state.set_state(Menu.main)


@router.message(Menu.main)
async def reg_three(message: Message, state: FSMContext):
    await message.answer(
        f"Введите основные блюда, которые вы едите в этот прием пиши в формате \n Блюдо1 [пробел дефис пробел] Кол-во ХЕ \n Блюдo2 [пробел дефис пробел] Кол-во ХЕ")
    await state.clear()


@router.message(Command('reg'))
async def reg_one(message: Message, state: FSMContext):
    await state.set_state(Reg.gender)
    msg = await message.answer_photo(photo=logo, caption="Введите Bаш пол", reply_markup=kb.gender_key)
    # msg = message.message_id
    await state.update_data(msg_id=(msg.message_id, message.chat.id))


@router.callback_query(F.data == 'man', Reg.gender)
async def reg_two(callback: CallbackQuery, state: FSMContext):
    text = "male"
    await state.update_data(gender=text)
    await state.set_state(Reg.height)
    await callback.message.delete_reply_markup()
    msg = await state.get_data()
    msg = msg["msg_id"]
    await bot.edit_message_caption(chat_id=msg[1], message_id=msg[0], caption="Введите Ваш рост")
    # await callback.message.edit_caption(caption="Введите Ваш рост")


@router.callback_query(F.data == 'women', Reg.gender)
async def reg_two(callback: CallbackQuery, state: FSMContext):
    text = "wom"
    await state.update_data(gender=text)
    msg = await state.get_data()
    msg = msg["msg_id"]
    await bot.edit_message_caption(chat_id=msg[1], message_id=msg[0], caption="Введите Ваш рост")
    # await callback.message.edit_caption(caption='Введите Ваш рост')


@router.message(Reg.height)
async def reg_three(message: Message, state: FSMContext):
    await state.update_data(height=message.text)
    await state.set_state(Reg.weight)
    msg = await state.get_data()
    msg = msg["msg_id"]
    await bot.edit_message_caption(chat_id=msg[1], message_id=msg[0], caption='Введите Ваш вес')
    # await message.answer_photo(photo=logo, caption="Введите Bаш вес")
    # await message.edit_caption(caption='Введите Ваш вес')


@router.message(Reg.weight)
async def reg_four(message: Message, state: FSMContext):
    await state.update_data(weight=message.text)
    await state.set_state(Reg.age)
    msg = await state.get_data()
    msg = msg["msg_id"]
    await bot.edit_message_caption(chat_id=msg[1], message_id=msg[0], caption='Введите Ваш возраст')


@router.message(Reg.age)
async def reg_five(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await state.set_state(Reg.meals)
    msg = await state.get_data()
    msg = msg["msg_id"]
    await bot.edit_message_caption(chat_id=msg[1], message_id=msg[0],
                                   caption="Введите время Ваших приемов пищи через пробел в формате: {ЧЧ:ММ}, а далее название приема пищи к каждому времени соответсвенно {завтрак обед ужин}")


@router.message(Reg.meals)
async def reg_five(message: Message, state: FSMContext):
    await state.update_data(meals=message.text.split(" "))
    id = message.from_user.id
    date_state = await state.get_data()
    print(date_state)
    create_user(id, date_state["gender"], date_state["height"], date_state["weight"],
                date_state["age"])
    for i in range(0, len(date_state["meals"]) // 2):
        time, name = date_state["meals"][i], date_state["meals"][i + len(date_state["meals"]) // 2]
        add_time(id, time, name)
        hours, minutes = map(int, time.split(":"))
        # print(tg_id, minutes, hours)
        sheduler.add_job(send_message_cron, trigger="cron", hour=hours,
                         minute=minutes,
                         start_date=dt.datetime.now(), kwargs={'bot': bot, "chat_id": id, "name": name})
    registered.append(id)
    await message.answer('Спасибо, регистрация завершена.')
    await state.clear()


@router.message(Command("reg_data"))
async def reg_data(message: Message):
    id = message.from_user.id
    print(get_user(id))
    print(get_times(id))
