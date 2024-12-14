from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from data_base import *

gender_key = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='МУЖ', callback_data='man'), InlineKeyboardButton(text='ЖЕН', callback_data='women')]
])

change_key = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Рост', callback_data='height'), InlineKeyboardButton(text='Вес', callback_data='weight')]
])


async def inline_eats(id):
    keyboard = ReplyKeyboardBuilder()
    sp = get_times(id)
    eats = []
    for i in sp:
        if i[3] not in eats:
            eats.append(i[3])
    for eat in eats:
        keyboard.add(KeyboardButton(text=eat))
    return keyboard.adjust(2).as_markup(resize_keyboard=True)


async def wards(users):
    keyboard = ReplyKeyboardBuilder()
    for user in users:
        keyboard.add(KeyboardButton(text=user))
    return keyboard.adjust(2).as_markup(resize_keyboard=True)

