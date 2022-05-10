from classes.manage_compositions import Compositions
from config import all_compositions_verses, all_compositions_poems, all_compositions_pieces
from config import LIMIT, EMBED_LIMIT
import discord
import sqlite3
from config import TABLE_NAME

Compositions = Compositions()

class ControlDialog:

	##Метод отсылки пользователю если он только зашёл на сервер
	def msg_on_join(self):
		name = "С товарищеским приветом, Маяковский"
		composition_title, composition_text, composition_name = Compositions.composition_by_name(name)

		return (composition_title, composition_text, composition_name)

	##Метод отсылки пользователю если он выходит с сервера
	def msg_on_remove(self):
		name = "Прощанье"
		composition_title, composition_text, composition_name = Compositions.composition_by_name(name)

		return (composition_title, composition_text, composition_name)

	##Найти случайное произведение
	def find_random_composition(self, find_verse=False, find_poem=False, find_piece=False, stop_list=[]):
		composition_title, composition_text = Compositions.random_composition_json(find_verse=find_verse, find_poem=find_poem, find_piece=find_piece)

		file_composition = (None, None)
		##Если содержимое для сообщения более лимита (4050 символов)
		if len(composition_title) + len(composition_text) + 50 >= EMBED_LIMIT:
			try:
				with open(f"safety_area/{composition_title}.txt", "w", encoding="utf-8") as file:
					file.write(composition_text)
			except:
				with open(f"safety_area/{composition_title}.txt", "w", encoding="cp1251") as file:
					file.write(composition_text)

			file_composition = (discord.File(f"safety_area/{composition_title}.txt"), f"safety_area/{composition_title}.txt")

		##Возвращаем название, текст и файл (на файл проверка внутри bot.py присутствует)
		return (composition_title, composition_text, file_composition)

	##Найти произведение по названию
	def find_composition_by_name(self, composition_name_from_user: str, stop_list: list=[]) -> tuple:
		composition_title, composition_text, file_composition = Compositions.composition_by_name(composition_name_from_user, stop_list=stop_list)
		return (composition_title, composition_text, file_composition)

	##Добавить произведение в стоп-лист
	@staticmethod
	def add_composition_to_stop_list(composition_name: str, stop_list: list):
		
		##Если стоп-лист не достиг максимальной своей длины - добавим в него произведение; Иначе - очистим стоп-лист
		if len(stop_list) < 2:
			stop_list.append(composition_name) ##Добавляем произведение в стоп-лист
		else:
			stop_list = []

		##Возвращаем стоп-лист
		return stop_list

	##Последняя новость в БД
	@staticmethod
	def get_last_new():
		with sqlite3.connect("data.db") as db:
			db.row_factory = sqlite3.Row
			cursor = db.cursor()

			news = cursor.execute(f"SELECT * FROM {TABLE_NAME}")
			new = cursor.fetchall()[0]

			date = new["date_time"]
			title = new["title"]
			content = new["content"]
			post_url = new["post_url"]
			image_url = new["image_url"]

			new = {
				"date_time": date,
				"title": title,
				"content": content,
				"post_url": post_url,
				"image_url": image_url
			}

			return new