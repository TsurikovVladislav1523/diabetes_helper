from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

gender_key = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='МУЖ', callback_data='man'), InlineKeyboardButton(text='ЖЕН', callback_data='women')]
])
