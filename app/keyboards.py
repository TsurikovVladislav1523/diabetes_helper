from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

gender_key = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='МУЖ', callback_data='man'), InlineKeyboardButton(text='ЖЕН', callback_data='women')]
])

change_key = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Рост', callback_data='height'), InlineKeyboardButton(text='Вес', callback_data='weight')], [InlineKeyboardButton(text='Время приемов пищи', callback_data='time_eat')]
])

# change_key = ReplyKeyboardMarkup(keyboard=[
#     [KeyboardButton(text='Рост'), KeyboardButton(text='Вес')], [KeyboardButton(text='Время приемов пищи')]
# ], resize_keyboard=True, input_field_placeholder="Выберете параметр, который хотите изменить", one_time_keyboard=True)