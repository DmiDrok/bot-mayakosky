from classes.manage_compositions import Compositions
from config import all_compositions_verses, all_compositions_poems, all_compositions_pieces
from config import LIMIT
import discord

class ControlDialog:

	##Метод отсылки пользователю если он только зашёл на сервер
	def msg_on_join(self):
		name = "С товарищеским приветом, Маяковский"
		composition_title, composition_text, composition_name = Compositions().search_by_name(name, amount=LIMIT, find_verse=True)

		return (composition_title, composition_text, composition_name)

	##Метод отсылки пользователю если он выходит с сервера
	def msg_on_remove(self):
		name = "Прощанье"
		composition_title, composition_text, composition_name = Compositions().search_by_name(name, amount=LIMIT, find_verse=True)

		return (composition_title, composition_text, composition_name)

	##Метод отсылки стихотворения в личные сообщения
	def verse_in_private_messages(self):
		composition_title, composition_text, composition_name = Compositions().random_composition(all_compositions=all_compositions_verses, find_verse=True)

		file_composition = None
	    ##Проверка на переполнение LIMIT суммы текста и названия стиха
		if len(composition_text) + len(composition_title) + 50 >= LIMIT:
			file_composition = discord.File(f"Произведения/Стихи/{composition_name}")
			
		return (composition_title, composition_text, composition_name, file_composition)

	##Найти случайный стих
	def find_random_verse(self):
		composition_title, composition_text, composition_name = Compositions().random_composition(all_compositions=all_compositions_verses, amount=LIMIT, find_verse=True)

		file_composition = None
		if len(composition_text) + len(composition_title) + 50 >= LIMIT:
			file_composition = discord.File(f"Произведения/Стихи/{composition_name}")

		return (composition_title, composition_text, composition_name, file_composition)

	##Найти случайную поэму
	def find_random_poem(self):
		composition_title, composition_text, composition_name = Compositions().random_composition(all_compositions=all_compositions_poems, amount=LIMIT, find_poem=True)

		file_composition = None
		if len(composition_text) + len(composition_title) + 50 >= LIMIT:
			file_composition = discord.File(f"Произведения/Поэмы/{composition_name}")

		return (composition_title, composition_text, composition_name, file_composition)

	##Найти случайную пьесу
	def find_random_piece(self):
		composition_title, composition_text, composition_name = Compositions().random_composition(all_compositions=all_compositions_pieces, amount=LIMIT, find_piece=True)

		file_composition = None
		if len(composition_text) + len(composition_title) + 50 >= LIMIT:
			file_composition = discord.File(f"Произведения/Пьесы/{composition_name}")

		return (composition_title, composition_text, composition_name, file_composition)