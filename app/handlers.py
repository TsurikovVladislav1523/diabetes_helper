import asyncio
import logging

import io
import os
import re

from statistic import *
import requests
from PIL import Image
from PIL.ExifTags import TAGS
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage
from data_base import *
from config import *
import app.keyboards as kb

from app.sheduler import *
import datetime as dt

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

storage = MemoryStorage()
bot = Bot(token=TOKEN)
router = Router()

sheduler.start()

registered = get_all_users()
#sheduler.add_job(send_message_cron, trigger="date", run_date=dt.datetime.now() + dt.timedelta(seconds=5),
#                 kwargs={'bot': bot, "chat_id": 1057505123, "name": "обед", "hours": 20, "minutes": 5, "state": FSMContext(storage=storage, key=StorageKey(bot_id=int(BOT_ID), chat_id=1057505123, user_id=1057505123, thread_id=None, business_connection_id=None, destiny='default'))})

def create_sheduler_stert():
    for tg_id, time, name in get_times_with_tg_id():
        hours, minutes = map(int, time.split(":"))
        # print(tg_id, minutes, hours)
        t_n = dt.datetime.now()
        t_d = dt.datetime.strptime(f"{t_n.year}:{t_n.month}:{t_n.day} {hours}:{minutes}", '%Y:%m:%d %H:%M') - t_n
        print(t_d)
        if t_n.hour * 100 + t_n.minute > hours * 100 + minutes:
            t_n = dt.datetime.now() + dt.timedelta(days=1)
            t_d = t_n - dt.datetime.strptime(
                f"{dt.datetime.now().year}:{dt.datetime.now().month}:{dt.datetime.now().day} {hours}:{minutes}",
                '%Y:%m:%d %H:%M')
            print(t_d)
        sheduler.add_job(send_message_cron, trigger="date", run_date=t_d + dt.datetime.now(),
                         kwargs={'bot': bot, "chat_id": tg_id, "name": name, "hours": hours, "minutes": minutes,
                                 "state": FSMContext(storage=storage,
                                                     key=StorageKey(bot_id=int(BOT_ID), chat_id=tg_id, user_id=tg_id,
                                                                    thread_id=None, business_connection_id=None,
                                                                    destiny='default'))})
        noise_sl[tg_id] = 0


class Reg(StatesGroup):
    gender = State()
    height = State()
    weight = State()
    age = State()
    meals = State()
    msg_id = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(START_TXT)
    print(state.storage, state.key)

    if message.from_user.id not in registered:
        await message.answer(
            "Вы не зарегистрированы в системе. Пожалуйста введите комаду /reg для прохождения регистрации")


class Photo(StatesGroup):
    sug_lvl = State()


@router.message(F.document)
async def get_photo(message: Message, state: FSMContext):
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
        date = dt.datetime.strptime(exifdata[306], '%Y:%m:%d %H:%M:%S')
        date = (f'{date.day}.{date.month}')
        t_d = dt.datetime.now() - dt.datetime.strptime(exifdata[306], '%Y:%m:%d %H:%M:%S')
        delta = t_d.seconds / 60
        if delta > 10:
            await message.answer(
                "Данное фото было сделано заранее, пожалуйста, отправьте актуальные данные")
        # создать задачу-напоминание
        else:
            await message.answer(
                f"Введите уровень сахара")
            await state.set_state(Photo.sug_lvl)
            await state.update_data(sug_lvl=(date, file_id))
            noise_sl[str(id)] = 0

    else:
        await message.answer(
            "Вы не зарегистрированы в системе. Пожалуйста введите комаду /reg для прохождения регистрации")


@router.message(Photo.sug_lvl)
async def reg_three(message: Message, state: FSMContext):
    '''ненужная функция, после подключения распознавалки удалить'''

    lvl = message.text
    id = message.from_user.id
    date = await state.get_data()
    add_measurement(id, date["sug_lvl"][1], date["sug_lvl"][0], sugar_level=lvl)
    await message.answer(
        f"Данные успешно сохранены, Дата: {date['sug_lvl'][0]}")
    await state.clear()


@router.message(Command("state"))
async def state(message: Message):
    id = message.from_user.id
    print(sugar_level(id))
    for photo in sugar_level(id):
        ph = FSInputFile(photo)
        await message.answer_photo(photo=ph)
        os.remove(photo)
    for photo in meal_stats(id):
        ph = FSInputFile(photo)
        await message.answer_photo(photo=ph)
        os.remove(photo)


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


@router.message(Command("get_id"))
async def change_p_one(message: Message, state: FSMContext):
    id = message.from_user.id
    await message.answer(text=str(id))


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
    if await check_height_input(message):
        id = message.from_user.id
        params = get_user(id)
        await state.clear()
        if txt != "НЕТ":
            update_user_h(id, txt)
    else:
        await send_try_again_message(message)

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
    if await check_height_input(message):
        id = message.from_user.id
        params = get_user(id)
        await state.clear()
        if txt != "НЕТ":
            update_user_w(id, txt)
    else:
        await send_try_again_message(message)


class Menu(StatesGroup):
    drinks = State()
    salats = State()
    soups = State()
    main = State()
    final = State()
    type = State()


@router.message(Command('create_menu'))
async def menu(message: Message, state: FSMContext):
    id = message.from_user.id
    await message.answer(
        f"Для составления Вашего рациона выберете название приема пищи, указанное при регистрации",
        reply_markup=await kb.inline_eats(id))
    await state.set_state(Menu.drinks)


@router.message(Menu.drinks)
async def reg_three(message: Message, state: FSMContext):
    await state.update_data(type=message.text)
    await message.answer(
        f"Введите напитки, которые вы пьете в этот прием пиши в формате \n Напиток1 [пробел дефис пробел] Кол-во ХЕ \n Напиток2 [пробел дефис пробел] Кол-во ХЕ",
        reply_markup=kb.ReplyKeyboardRemove())
    await state.set_state(Menu.salats)


@router.message(Menu.salats)
async def reg_three(message: Message, state: FSMContext):
    id = message.from_user.id
    if await check_food_input(message):
        text = message.text.split("\n")
        type = await state.get_data()
        type = type["type"]
        for i in text:
            name, xe = i.split(" - ")
            add_eat(id, name, "drinks", type, xe)
        await message.answer(
            f"Введите салаты, которые вы едите в этот прием пиши в формате \n Салат1 [пробел дефис пробел] Кол-во ХЕ \n Салат2 [пробел дефис пробел] Кол-во ХЕ")
        await state.set_state(Menu.soups)
    else:
        await send_try_again_message(message)

@router.message(Menu.soups)
async def reg_three(message: Message, state: FSMContext):
    id = message.from_user.id
    if await check_food_input(message):
        text = message.text.split("\n")
        type = await state.get_data()
        type = type["type"]
        for i in text:
            name, xe = i.split(" - ")
            add_eat(id, name, "salats", type, xe)
        await message.answer(
            f"Введите супы или каши, которые вы едите в этот прием пиши в формате \n Суп1 [пробел дефис пробел] Кол-во ХЕ \n Каша2 [пробел дефис пробел] Кол-во ХЕ")
        await state.set_state(Menu.main)
    else:
        await send_try_again_message(message)


@router.message(Menu.main)
async def reg_three(message: Message, state: FSMContext):
    id = message.from_user.id
    if await check_food_input(message):
        text = message.text.split("\n")
        type = await state.get_data()
        type = type["type"]
        for i in text:
            name, xe = i.split(" - ")
            add_eat(id, name, "soups", type, xe)
        await message.answer(
            f"Введите основные блюда, которые вы едите в этот прием пиши в формате \n Блюдо1 [пробел дефис пробел] Кол-во ХЕ \n Блюдo2 [пробел дефис пробел] Кол-во ХЕ")
        await state.set_state(Menu.final)
    else:
        await send_try_again_message(message)


@router.message(Menu.final)
async def reg_three(message: Message, state: FSMContext):
    id = message.from_user.id
    if await check_food_input(message):
        text = message.text.split("\n")
        type = await state.get_data()
        type = type["type"]
        for i in text:
            name, xe = i.split(" - ")
            add_eat(id, name, "main", type, xe)
        await message.answer(
            f"Составление рациона завершено")
        await state.clear()
    else:
        await send_try_again_message(message)

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


@router.callback_query(F.data == 'women', Reg.gender)
async def reg_two(callback: CallbackQuery, state: FSMContext):
    text = "wom"
    await state.update_data(gender=text)
    msg = await state.get_data()
    msg = msg["msg_id"]
    await bot.edit_message_caption(chat_id=msg[1], message_id=msg[0], caption="Введите Ваш рост")


@router.message(Reg.height)
async def reg_three(message: Message, state: FSMContext):
    if await check_height_input(message):
        await state.update_data(height=message.text)
        await state.set_state(Reg.weight)
        msg = await state.get_data()
        msg = msg["msg_id"]
        await bot.edit_message_caption(chat_id=msg[1], message_id=msg[0], caption='Введите Ваш вес')
        await message.answer(text="Введите Bаш вес")
        # await message.edit_caption(caption='Введите Ваш вес')
    else:
        await send_try_again_message(message)


@router.message(Reg.weight)
async def reg_four(message: Message, state: FSMContext):
    if await check_weight_input(message):
        await state.update_data(weight=message.text)
        await state.set_state(Reg.age)
        msg = await state.get_data()
        msg = msg["msg_id"]
        await bot.edit_message_caption(chat_id=msg[1], message_id=msg[0], caption='Введите Ваш возраст')
        await message.answer(text="Введите Bаш возраст")
    else:
        await send_try_again_message(message)

@router.message(Reg.age)
async def reg_five(message: Message, state: FSMContext):
    if await check_age_input(message):
        await state.update_data(age=message.text)
        await state.set_state(Reg.meals)
        msg = await state.get_data()
        msg = msg["msg_id"]
        await bot.edit_message_caption(chat_id=msg[1], message_id=msg[0],
                                       caption="Введите время Ваших приемов пищи на отдельных строках в формате: {ЧЧ:ММ [пробел дефис пробел] название приема пищи}")
        await message.answer(
            text='Введите время Ваших приемов пищи на отдельных строках в формате: {ЧЧ:ММ [пробел дефис пробел] название приема пищи}')
    else:
        await send_try_again_message(message)


@router.message(Reg.meals)
async def reg_five(message: Message, state: FSMContext):
    if await check_meal_input(message):
        await state.update_data(meals=message.text.split("\n"))
        id = message.from_user.id
        date_state = await state.get_data()
        print(date_state)
        create_user(id, date_state["gender"], date_state["height"], date_state["weight"],
                    date_state["age"])
        for i in date_state["meals"]:
            time, name = i.split(" - ")
            add_time(id, time, name)
            hours, minutes = map(int, time.split(":"))
            # print(tg_id, minutes, hours)
            t_n = dt.datetime.now()
            t_d = dt.datetime.strptime(f"{t_n.year}:{t_n.month}:{t_n.day} {hours}:{minutes}", '%Y:%m:%d %H:%M') - t_n
            print(t_d)
            if t_n.hour * 100 + t_n.minute > hours * 100 + minutes:
                t_n = dt.datetime.now() + dt.timedelta(days=1)
                t_d = t_n - dt.datetime.strptime(
                    f"{dt.datetime.now().year}:{dt.datetime.now().month}:{dt.datetime.now().day} {hours}:{minutes}",
                    '%Y:%m:%d %H:%M')
                print(t_d)
            sheduler.add_job(send_message_cron, trigger="date", run_date=t_d + dt.datetime.now(),
                             kwargs={'bot': bot, "chat_id": id, "name": name, "hours": hours, "minutes": minutes,
                                     "state": FSMContext(storage=storage,
                                                         key=StorageKey(bot_id=int(BOT_ID), chat_id=id, user_id=id,
                                                                        thread_id=None, business_connection_id=None,
                                                                        destiny='default'))})
        registered.append(id)
        noise_sl[id] = 0
        print(registered)
        await message.answer('Спасибо, регистрация завершена.')
        await state.clear()
    else:
        await send_try_again_message(message)

async def send_code(code, telegram_id):
    await bot.send_message(chat_id=telegram_id, text=f"Ваш код подтверждения: {code}")


'''Блок смотрящего'''


class Obs(StatesGroup):
    id = State()


@router.message(Command('add_observer'))
async def add_obs(message: Message, state: FSMContext):
    await message.answer('Для привязки к Вам смотрящего введите его телеграм id')
    print("Для привязки к Вам смотрящего введите его телеграм id")
    await state.set_state(Obs.id)


@router.message(Obs.id)
async def add_obs(message: Message, state: FSMContext):
    obs_id = message.text
    id = message.from_user.id
    add_oserver(id, obs_id)
    await state.clear()


class Ward(StatesGroup):
    id = State()


@router.message(Command("ward_stat"))
async def add_obs(message: Message, state: FSMContext):
    id = message.from_user.id
    users = get_obs_id(id)
    await message.answer(
        f"Выберете id подопечного, у которого хотите посмотреть статистику",
        reply_markup=await kb.wards(users))
    await state.set_state(Ward.id)


@router.message(Ward.id)
async def add_obs(message: Message, state: FSMContext):
    id = message.text
    await message.answer(
        f"Статистика пользователя {id}:",
        reply_markup=kb.ReplyKeyboardRemove())

    for photo in sugar_level(id):
        ph = FSInputFile(photo)
        await message.answer_photo(photo=ph)
        os.remove(photo)
    for photo in meal_stats(id):
        ph = FSInputFile(photo)
        await message.answer_photo(photo=ph)
        os.remove(photo)

    await state.clear()

@router.message(Command("ward_image"))
async def image(message: Message, state: FSMContext):
    pass
'''Конец блока'''

'''Блок с шедулером'''


@router.message(M.inp)
async def process_eaten(message: types.Message, state: FSMContext):
    id = message.from_user.id
    eaten_indices = message.text.split(' ')
    eaten_indices = [int(index.strip()) for index in eaten_indices if index.strip().isdigit()]
    xes = await state.get_data()
    xes, type = xes["xes"], xes["type"]
    print(xes, type)
    date = f"{dt.datetime.now().day}.{dt.datetime.now().month}"
    xe = 0
    for i in eaten_indices:
        xe += xes[i]
    await state.clear()
    await message.answer("Отправьте фотографию вашего глюкометра в формате документа (без сжатия)")
    add_meal(id, type, xe, date)


'''Конец блока шедулер'''


@router.message(Command("reg_data"))
async def reg_data(message: Message):
    id = message.from_user.id
    print(get_user(id))
    print(get_times(id))


'''Проверки ввода'''


async def send_try_again_message(message: Message):
    await message.answer('Неверные данные, попробуйте ввести снова')


async def check_height_input(message: Message):
    txt = message.text
    if txt == 'НЕТ':
        return True
    try:
        number = int(txt)
        if 10 < number < 252:
            return True
        else:
            return False
    except:
        return False


async def check_weight_input(message: Message):
    txt = message.text
    if txt == 'НЕТ':
        return True
    try:
        number = int(txt)
        if 20 < number < 646:
            return True
        else:
            return False
    except:
        return False


async def check_age_input(message: Message):
    txt = message.text
    if txt == 'НЕТ':
        return True
    try:
        number = int(txt)
        if 3 < number < 150:
            return True
        else:
            return False
    except:
        return False


async def check_food_input(message: Message):
    pattern = r'^[A-Za-zА-Яа-яёЁ\s]+ - \d+$'

    txt = message.text
    lines = txt.strip().split('\n')

    for line in lines:
        if not bool(re.match(pattern, line)):
            return False
    return True


async def check_meal_input(message: Message):
    # Регулярное выражение для проверки формата времени и приема пищи
    pattern = r'^(\d{2}):(\d{2}) - .+$'

    txt = message.text.strip()  # Убираем лишние пробелы в начале и конце
    lines = txt.split('\n')  # Разделяем на строки по символу новой строки

    # Проходим по каждой строке и проверяем ее
    for line in lines:
        # Убираем лишние пробелы по краям каждой строки
        line = line.strip()

        # Проверка на наличие дополнительной временной метки в одной строке
        if line.count(' - ') > 1:
            return False

        # Проверка строки на соответствие регулярному выражению
        match = re.match(pattern, line)
        if not match:
            return False

        hours = int(match.group(1))  # Часы
        minutes = int(match.group(2))  # Минуты

        # Проверка корректности времени
        if not (0 <= hours <= 23 and 0 <= minutes <= 59):
            return False

        # Получаем название приема пищи после дефиса
        meal_name = line.split(' - ')[1].strip()

        # Проверка, что название не пустое
        if not meal_name:
            return False

        # Проверка на наличие символов новой строки в названии
        if '\n' in meal_name or '\r' in meal_name:
            return False

    return True



# async def check_meal_input(message: Message):
#     pattern = r'^(\d{2}):(\d{2}) - .+$'
#
#     txt = message.text
#     lines = txt.strip().split('\n')
#
#     for line in lines:
#         if '/n' in line:
#             return False
#         match = re.match(pattern, line)
#         if not match:
#             return False
#
#         hours = int(match.group(1))
#         minutes = int(match.group(2))
#
#         if not (0 <= hours <= 23 and 0 <= minutes <= 59):
#             return False
#
#     print(lines)
#     return True


async def check_id_input(message: Message):
    text = message.text
    return len(text) == 10 and text.isdigit()

