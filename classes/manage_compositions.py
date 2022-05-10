import random
from config import LIMIT, EMBED_LIMIT
import json
import discord

class Compositions:

    def __init__(self):
        ##Атрибуты класса Compositions для дальнейшего взаимодействия при поиске и т.д.
        self.all_compositions_json = json.load(open("all_compositions.json", "r", encoding="utf-8"))
        self.all_compositions = {
            "Стихи": self.all_compositions_json["Стихи"],
            "Поэмы": self.all_compositions_json["Поэмы"],
            "Пьесы": self.all_compositions_json["Пьесы"]
        }

        self.json_for_check = self.__CreateDictComps()

    ##Рандомный стих через JSON
    def random_composition_json(self, find_verse=False, find_poem=False, find_piece=False, stop_list=[]):
        key_composition = None
        if find_verse == True:
            key_composition = "Стихи"
        elif find_poem == True:
            key_composition = "Поэмы"
        elif find_piece == True:
            key_composition = "Пьесы"

        ##Если указан тип композиции
        if key_composition != None:
            random_verse_title = random.choice(tuple(enumerate(self.all_compositions_json[key_composition])))[1]
            random_verse_text = self.all_compositions_json[key_composition][random_verse_title]

            ##Пока название произведения есть в стоп-листе - будем выбирать рандомное произведение снова
            while random_verse_title in stop_list:
                random_verse_title = random.choice(tuple(enumerate(self.all_compositions_json[key_composition])))[1]
                random_verse_text = self.all_compositions_json[key_composition][random_verse_title]
            


            ##Возвращаем название произведения и его текст
            return (random_verse_title, random_verse_text)

    ##Найти произведение по названию
    def composition_by_name(self, composition_name_from_user, stop_list=[]):
        composition_name_from_user_arr = composition_name_from_user.lower().replace("!", "").replace("?", "").replace(".", "").replace(",", "").strip().split(" ")
        composition_key_from_user = composition_name_from_user[0].upper() + composition_name_from_user[1::].lower() ##Ключ - первая буква заглавная - все остальные малые (не идеальный, но на некоторые произведения действительно срабатывает)

        ##Три переменные которые мы вернём этой функцией
        composition_name_correctly = None
        composition_text = None
        file_composition = None

        double_break = False

        ##Если всё совпадает в названии введённом пользователем и в названии в списке произведений
        for type_composition in ["Стихи", "Поэмы", "Пьесы"]:
            for key in self.all_compositions_json[type_composition]:
                for i in composition_name_from_user_arr:
                    if i in key.lower().replace("!", "").replace("?", "").replace(".", "").replace(",", "").strip().split():
                        if key.lower().replace("!", "").replace("?", "").replace(".", "").replace(",", "").strip().split().index(i) == key.lower().replace("!", "").replace("?", "").replace(".", "").replace(",", "").strip().split().index(key.lower().replace("!", "").replace("?", "").replace(".", "").replace(",", "").strip().split()[-1]):
                            print("Я ТУТ0")
                            composition_name_correctly = key
                            composition_text = self.all_compositions_json[type_composition][key]

                            if len(composition_name_correctly) + len(composition_text) >= EMBED_LIMIT:
                                file_composition = self.__CreateFile(composition_name_correctly, composition_text)

                            return (composition_name_correctly, composition_text, file_composition)
                            continue
                    else:
                        break

        ##Пробегаемся, и, если пользователь ввёл название произведения правильно - отдаём ему
        composition_name_to_search = composition_name_from_user.lower().replace("!", "").replace("?", "").replace(".", "").replace(",", "").strip()
        for type_composition in ["Стихи", "Поэмы", "Пьесы"]:
            if composition_name_to_search in self.json_for_check[type_composition]:
                composition_name_correctly = tuple(enumerate(self.json_for_check[type_composition][composition_name_to_search]))[0][1]
                composition_text = self.json_for_check[type_composition][composition_name_to_search][composition_name_correctly]
                
                ##Если длина контента превышает максимальную вместимость Эмбеда
                if len(composition_name_correctly) + len(composition_text) >= EMBED_LIMIT:
                    file_composition = self.__CreateFile(composition_name_correctly, composition_text)

                return (composition_name_correctly, composition_text, file_composition)

        ##Ищем среди всех произведений
        for key in ["Стихи", "Поэмы", "Пьесы"]:
            for composition_name_correctly in self.all_compositions_json[key]:
                if self.__IsAlike(composition_name_correctly.lower().replace("!", "").replace("?", "").replace(".", "").replace(",", "").strip(), composition_name_from_user.lower().replace("!", "").replace("?", "").replace(".", "").replace(",", "").strip()) == True and composition_name_correctly not in stop_list: ##Если есть схожесть в введённом названии от пользователя и настоящем названии произведения
                    
                    composition_text = self.all_compositions_json[key][composition_name_correctly]
                    
                    ##Если длина контента превышает максимальную вместимость Эмбеда - делаем файл и отсылаем его далее
                    if len(composition_name_correctly) + len(self.all_compositions_json[key][composition_name_correctly]) >= EMBED_LIMIT\
                    or composition_key_from_user in self.all_compositions_json[key]:
                        file_composition = self.__CreateFile(composition_name_correctly, composition_text)

                    return (composition_name_correctly, composition_text, file_composition)

        ##Сюда мы попадём если произведение до сих пор не было найдено
        for key in ["Стихи", "Поэмы", "Пьесы"]:
            for composition_name_correctly in self.all_compositions_json[key]:
                if composition_name_from_user.lower()[0] == composition_name_correctly.lower()[0] and composition_name_correctly not in stop_list:
                    
                    composition_text = self.all_compositions_json[key][composition_name_correctly]

                    ##Если длина контента превышает максимальную вместимость Эмбеда
                    if len(composition_name_correctly) + len(self.all_compositions_json[key][composition_name_correctly]) >= EMBED_LIMIT:
                        file_composition = self.__CreateFile(composition_name_correctly, composition_text)

                    return (composition_name_correctly, composition_text, file_composition)

        ##Если произведение не было найдено до сих пор - чистим стоп лист и перезываем метод поиска
        if composition_name_correctly == None:
            stop_list = []
            self.composition_by_name(composition_name_from_user, stop_list=stop_list)

        ##Возвращаем название, текст и файл произведения
        return (composition_name_correctly, composition_text, file_composition)

    ##Статический метод для проверки схожести введённого пользователем названия с тем, что есть в списке всех названий
    @staticmethod
    def __IsAlike(composition_name_correctly: str, composition_name_from_user: str):
        composition_name_correctly = composition_name_correctly.lower()
        composition_name_from_user = composition_name_from_user.lower()

        name_from_user_arr = composition_name_from_user.split()
        name_correctly_arr = composition_name_correctly.split()

        for i in name_from_user_arr:
            if i in name_correctly_arr:
                continue
            else:
                return False

        return True

    ##Статический метод для проверки на длину текста с последующим созданием файла и отсылки далее его пользователю
    @staticmethod
    def __CreateFile(composition_name: str, to_write: str):
        ##Открываем и записываем
        def open_to_write(encoding):
            with open(f"safety_area/{composition_name}.txt", "w", encoding="utf-8") as file:
                file.write(to_write)

        ##Для избавления от ошибок и стабильной последующей работой
        encoding = "utf-8"
        try:
            open_to_write(encoding=encoding)
        except:
            encoding = "cp1251"
            open_to_write(encoding=encoding)

        return discord.File(f"safety_area/{composition_name}.txt")

    ##Словарь вида {мал.название: {Большое название: текст произведения}}
    def __CreateDictComps(self):
        dict_comps = {}
        import time
        for type_composition in ["Стихи", "Поэмы", "Пьесы"]:
            for comp in self.all_compositions_json[type_composition]:
                if type_composition in dict_comps:
                    dict_comps[type_composition].update({comp.lower().replace("!", "").replace("?", "").replace(".", "").replace(",", "").strip(): {comp: self.all_compositions_json[type_composition][comp]}})
                else:
                    dict_comps[type_composition] = {comp.lower().replace("!", "").replace("?", "").replace(".", "").replace(",", "").strip(): {comp: self.all_compositions_json[type_composition][comp]}}

        return dict_comps