import os

TOKEN = "OTcxODUxNzQ2NDMzNDUwMDY0.G5tiHi.GdAsGi7ZvDRLIoJK5c9mesB1hdw5XEsuJQu__g"
PREFIX = "."
LIMIT = 2000
EMBED_LIMIT = 4050

##Название таблицы sqlite3
TABLE_NAME = "game_news"

##Секретный канал для отправки новостей
SECRET_CHANNEL_TO_NEWS = ["новости-hoi4", "новости-хой4"]

##Список всех стихотворений из папки 'Стихи'
all_compositions_verses = os.listdir("Произведения/Стихи/")

##Список всех поэм из папки 'Поэмы'
all_compositions_poems = os.listdir("Произведения/Поэмы/")

##Список всех пьес из папки 'Пьесы'
all_compositions_pieces = os.listdir("Произведения/Пьесы/")