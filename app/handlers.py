import io
import os
import re

import requests
from PIL import Image
import matplotlib.pyplot as plt

from config import *
import app.keyboards as kb

from app.sheduler import *
import datetime as dt
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Bot, F, Router
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

sheduler.add_job(send_message_cron, trigger="cron", hour=17,
                 minute=50,
                 start_date=dt.datetime.now(), kwargs={'bot': bot, "chat_id": 1057505123, "name": "обед", "state": FSMContext})

for tg_id, time, name in get_times_with_tg_id():
    hours, minutes = map(int, time.split(":"))
    # print(tg_id, minutes, hours)
    sheduler.add_job(send_message_cron, trigger="cron", hour=hours,
                     minute=minutes,
                     start_date=dt.datetime.now(), kwargs={'bot': bot, "chat_id": id, "name": name, "state": FSMContext})


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
        f"Данные успешно сохранены, Время: {date['sug_lvl'][0]}")
    await state.clear()


@router.message(Command("state"))
async def state(message: Message):
    id = message.from_user.id
    all_photo = get_measurement(id)
    slovar = {}
    for ph in all_photo:
        date = ph[4]
        if date in slovar:
            slovar[date].append(float(ph[2]))
        else:
            slovar[date] = []
            slovar[date].append(float(ph[2]))
    x = []
    y = []
    for key in slovar:
        sp = slovar[key]
        x.append(key)
        res = round(sum(sp) / len(sp), 1)
        y.append(res)
    # ax = plt.axes()
    # ax.set_facecolor("dimgray")
    plt.title("Среднее значение уровня сахара за каждый из дней")  # заголовок
    plt.xlabel("День")  # ось абсцисс
    plt.ylabel("Уровень сахара")  # ось ординат
    plt.grid(True)  # включение отображение сетки
    plt.minorticks_on()
    plt.plot(x, y, "b--", marker='o', markersize=4)  # построение графика
    plt.savefig('images/1.png')
    graph = FSInputFile("images/1.png")
    await message.answer_photo(photo=graph)
    os.remove("images/1.png")

    plt.clf()
    plt.minorticks_on()
    plt.bar(x, y, label='Уровень сахара', color='skyblue')  # Параметр label позволяет задать название величины для легенды
    plt.xlabel('День')
    plt.ylabel('Уровень сахара')
    plt.title('Среднее значение уровня сахара за каждый из дней')
    plt.legend(loc='lower left')
    for c in range(len(y)):
        plt.annotate(y[c], xy=(c - 0.25, y[c] - 0.5), color='black')
    plt.savefig('images/1.png')
    graph = FSInputFile("images/1.png")
    await message.answer_photo(photo=graph)
    os.remove("images/1.png")
    plt.clf()


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
        f"Для составления Вашего рациона выберете название приема пищи, указанное при регистрации", reply_markup=await kb.inline_eats(id))
    await state.set_state(Menu.drinks)


@router.message(Menu.drinks)
async def reg_three(message: Message, state: FSMContext):
    await state.update_data(type=message.text)
    await message.answer(
        f"Введите напитки, которые вы пьете в этот прием пиши в формате \n Напиток1 [пробел дефис пробел] Кол-во ХЕ \n Напиток2 [пробел дефис пробел] Кол-во ХЕ", reply_markup=kb.ReplyKeyboardRemove())
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
        await message.answer(text='Введите время Ваших приемов пищи на отдельных строках в формате: {ЧЧ:ММ [пробел дефис пробел] название приема пищи}')
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
            sheduler.add_job(send_message_cron, trigger="cron", hour=hours,
                             minute=minutes,
                             start_date=dt.datetime.now(), kwargs={'bot': bot, "chat_id": id, "name": name, "state": state})
        registered.append(id)
        print(registered)
        await message.answer('Спасибо, регистрация завершена.')
        await state.clear()
    else:
        await send_try_again_message(message)

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
    if check_id_input(message):
        obs_id = message.text
        id = message.from_user.id
        add_oserver(id, obs_id)
        await state.clear()
    else:
        await send_try_again_message(message)


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
    if check_id_input(message):
        id = message.text
        await message.answer(
            f"Статистика пользователя {id}:",
            reply_markup=kb.ReplyKeyboardRemove())

        all_photo = get_measurement(id)
        slovar = {}
        for ph in all_photo:
            date = ph[4]
            if date in slovar:
                slovar[date].append(float(ph[2]))
            else:
                slovar[date] = []
                slovar[date].append(float(ph[2]))
        x = []
        y = []
        for key in slovar:
            sp = slovar[key]
            x.append(key)
            res = round(sum(sp) / len(sp), 1)
            y.append(res)
        # ax = plt.axes()
        # ax.set_facecolor("dimgray")
        plt.title("Среднее значение уровня сахара за каждый из дней")  # заголовок
        plt.xlabel("День")  # ось абсцисс
        plt.ylabel("Уровень сахара")  # ось ординат
        plt.grid(True)  # включение отображение сетки
        plt.minorticks_on()
        plt.plot(x, y, "b--", marker='o', markersize=4)  # построение графика
        plt.savefig('images/1.png')
        graph = FSInputFile("images/1.png")
        await message.answer_photo(photo=graph)
        os.remove("images/1.png")

        plt.clf()
        plt.minorticks_on()
        plt.bar(x, y, label='Уровень сахара',
                color='skyblue')  # Параметр label позволяет задать название величины для легенды
        plt.xlabel('День')
        plt.ylabel('Уровень сахара')
        plt.title('Среднее значение уровня сахара за каждый из дней')
        plt.legend(loc='lower left')
        for c in range(len(y)):
            plt.annotate(y[c], xy=(c - 0.25, y[c] - 0.5), color='black')
        plt.savefig('images/1.png')
        graph = FSInputFile("images/1.png")
        await message.answer_photo(photo=graph)
        os.remove("images/1.png")
        plt.clf()

        await state.clear()
    else:
        await send_try_again_message(message)

'''Конец блока'''

'''Блок с шедулером'''


@router.message(M.inp)
async def process_eaten(message: types.Message, state: FSMContext):
    eaten_indices = message.text.split(' ')
    eaten_indices = [int(index.strip()) for index in eaten_indices if index.strip().isdigit()]
    await state.clear()
    print(eaten_indices)


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
    pattern = r'^(\d{2}):(\d{2}) - .+$'

    txt = message.text
    lines = txt.strip().split('\n')

    for line in lines:
        match = re.match(pattern, line)
        if not match:
            return False

        hours = int(match.group(1))
        minutes = int(match.group(2))

        if not (0 <= hours <= 23 and 0 <= minutes <= 59):
            return False

    return True


async def check_id_input(message: Message):
    text = message.text
    return len(text) == 10 and text.isdigit()

