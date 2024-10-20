from aiogram import Bot
async def send_message_cron(bot: Bot, chat_id: int):
    await bot.send_message(chat_id, "Отправьте фотографию Вашего уровня сахара")