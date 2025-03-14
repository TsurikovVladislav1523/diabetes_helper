from aiogram import Bot

from aiogram import Bot, types
from data_base import *
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import datetime as dt
noise_sl = {}
verif_ids = {}
sheduler = AsyncIOScheduler(timezone="Europe/Moscow")


class M(StatesGroup):
    inp = State()

async def send_noise_message(bot: Bot, chat_id: int):
    if noise_sl[str(chat_id)] != 0:
        if noise_sl[str(chat_id)] == 3:
            await bot.send_message(chat_id, f"Отправьте фотографию вашего глюкометра.\nСообщение о Вашей халатности будет направлено Вашему наблюдателю!")
            noise_sl[str(chat_id)] = 0
            id = get_obs_id_1(chat_id)[0][0]
            await bot.send_message(id, f"Пользователь {chat_id} игнорирует отправку данных")
            noise_sl[str(chat_id)] = 0
        else:
            await bot.send_message(chat_id,f"Отправьте фотографию вашего глюкометра.\nПовторяю {noise_sl[str(chat_id)]} раз. На 3-ий раз сообщение о Вашей халатности будет направлено Вашему наблюдателю!")

            sheduler.add_job(send_noise_message, trigger="date", run_date=dt.datetime.now() + dt.timedelta(minutes=5), # Для демострации
                             kwargs={'bot': bot, "chat_id": chat_id})
            noise_sl[str(chat_id)] += 1




async def send_message_cron(bot: Bot, chat_id: int, name: str, hours, minutes, state: FSMContext):
    '''Отправка меню, сохранение в таблицу'''
    # Подключение к базе данных
    records = get_menu(chat_id, name)
    if not records:
        await bot.send_message(chat_id, "У вас нет записей в меню. Отправьте фотографию вашего глюкометра")
        return
    # Формирование сообщения с номерами позиций
    menu_message = "Ваше меню:\n"
    k = 0
    xes = {}
    for index, (name1, type, xe) in enumerate(records, start=1):
        if k == 0:
            menu_message += ("Напитки:\n")
            k += 1
        if k == 1 and type == "salats":
            menu_message += ("Cалаты:\n")
            k += 1
        if k == 2 and type == "soups":
            menu_message += ("Супы и каши:\n")
            k += 1
        if k == 3 and type == "main":
            menu_message += ("Основные блюда:\n")
            k += 1
        menu_message += (f"    {index}: {name1} ({xe} XE)\n")
        xes[index] = xe

    print(state.storage, state.key)
    await bot.send_message(chat_id, menu_message)
    await bot.send_message(chat_id, "Введите номера позиций, которые вы съели, через пробел:")
    await state.set_state(M.inp)  # Ожидание ввода пользователя
    await state.update_data(xes=xes, type=name)
    sheduler.add_job(send_noise_message, trigger="date", run_date=dt.datetime.now() + dt.timedelta(minutes=5),
                     kwargs={'bot': bot, "chat_id": chat_id})
    noise_sl[str(chat_id)] = 1
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
                     kwargs={'bot': bot, "chat_id": chat_id, "name": name, "hours": hours, "minutes": minutes,
                             "state": state})

async def send_control_cron(bot: Bot, chat_id: int):
    '''Отправка меню, сохранение в таблицу'''
    # Подключение к базе данных
    await bot.send_message(chat_id, f"Было зафиксированно отклонение от нормы. Пожалуйста, повторите измерение и отправьте данные")
    sheduler.add_job(send_noise_message, trigger="date", run_date=dt.datetime.now() + dt.timedelta(minutes=5),
                     kwargs={'bot': bot, "chat_id": chat_id})
    noise_sl[str(chat_id)] = 1
