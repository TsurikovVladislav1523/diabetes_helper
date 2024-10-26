from aiogram import Bot
async def send_message_cron(bot: Bot, chat_id: int, name: str):
    await bot.send_message(chat_id, f"Отправьте фотографию Вашего уровня сахара и выберите из своего рациона, что Вы ели на {name}")