import random
from config import LIMIT

class Compositions:

    ##Взять случайное произведение (его название и текст)
    def random_composition(self, amount:int = LIMIT, all_compositions=None, find_verse=False, find_poem=False, find_piece=False) -> tuple:
        composition_name = random.choice(all_compositions)
        encoding = "utf-8"

        ##Функция считывания содержимого файла
        def read_composition(encoding: str):
            ##Берём тип произведения
            type_composition = None
            if find_verse == True:
                type_composition = "Стихи"
            elif find_poem == True:
                type_composition = "Поэмы"
            elif find_piece == True:
                type_composition = "Пьесы"

            ##Открываем случайное произведение
            with open(f"Произведения/{type_composition}/{composition_name}", "r", encoding=encoding) as file:
                composition_title = composition_name.replace(".txt", "")
                composition_text = file.read()

                return (composition_title, composition_text, composition_name)

        ##Оборачиваем в try-except из-за исключений связанных с кодировками файлов
        try:
            return read_composition(encoding=encoding)
        except Exception as error:
            encoding = "cp1251"
            return read_composition(encoding=encoding)

    ##Поиск по названию
    def search_by_name(self, composition_name:str, amount:int = LIMIT, find_verse=False, find_poem=False) -> tuple:
        composition_name = composition_name + ".txt"
        encoding = "utf-8"

        ##Функция считывания содержимого файла
        def read_composition(encoding:str):
            ##Берём тип произведения
            type_composition = None
            if find_verse == True:
                type_composition = "Стихи"
            elif find_poem == True:
                type_composition = "Поэмы"

            with open(f"Произведения/{type_composition}/{composition_name}", "r", encoding=encoding) as file:
                composition_title = composition_name.replace(".txt", "")
                print(composition_title)
                composition_text = file.read()

                return (composition_title, composition_text, composition_name)

        ##Оборачиваем в try-except из-за исключений связанных с кодировками файлов
        try:
            return read_composition(encoding)
        except Exception as error:         
            encoding = "cp1251"
            return read_composition(encoding=encoding)