from aiogram import Bot
async def send_message_cron(bot: Bot, chat_id: int, name: str):
    await bot.send_message(chat_id, f"Выберите из своего рациона, что Вы ели на {name}, а потом отправьте фотографию глюкометра")
    '''Отправка меню, сохранение в таблицу'''


from aiogram import Bot, types
from data_base import *
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

class M(StatesGroup):
    inp = State()
#     await bot.send_message(chat_id, f"Выберите из своего рациона, что Вы ели на {name}, а потом отправьте фотографию глюкометра")

async def send_message_cron(bot: Bot, state: FSMContext, chat_id: int, name: str, ):
    '''Отправка меню, сохранение в таблицу'''
    # Подключение к базе данных
    records = get_menu(chat_id, name)
    if not records:
        await bot.send_message(chat_id, "У вас нет записей в меню. Отправьте фотографию вашего глюкометра")
        return

    # Формирование сообщения с номерами позиций
    menu_message = "Ваше меню:\n"
    print(records)
    for index, (_, food_id, food_name, eat_name) in enumerate(records, start=1):
        menu_message += f"{index}. {food_name} ({eat_name})\n"
    await bot.send_message(chat_id, menu_message)
    await bot.send_message(chat_id, "Введите номера позиций, которые вы съели, через пробел:")
    await state.set_state(M.inp)
    # Ожидание ввода пользователя

