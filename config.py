from aiogram.types import FSInputFile

TOKEN = '6084071502:AAG8QyyaCr-HLOiVPaGsF6_GSaN1TluBzz0'
START_TXT = 'Доброго времени суток! Добро пожаловать на сервис по помощи и отслеживанию пациентов, страдающий сахарным диабетом. \n\nЗдесь можно контроллировать измерение сахара в крови, потребление ХЕ, а также получать статистику об уровне сахара за последнюю неделю.'
URI = f'https://api.telegram.org/file/bot{TOKEN}/'

logo = FSInputFile("images/logo.png")