from aiogram import Bot
async def send_message_cron(bot: Bot, chat_id: int, name: str):
    await bot.send_message(chat_id, f"Выберите из своего рациона, что Вы ели на {name}, а потом отправьте фотографию глюкометра")
    '''Отправка меню, сохранение в таблицу'''