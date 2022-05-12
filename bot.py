import discord
from discord.ext import commands
from config import TOKEN, PREFIX
from config import LIMIT, EMBED_LIMIT
from config import all_compositions_verses, all_compositions_poems, all_compositions_pieces
import asyncio
import re
from classes.control_dialog_output import ControlDialog
from classes.manage_compositions import Compositions
import os
import random
import requests
from bs4 import BeautifulSoup as BS
import sqlite3
from config import TABLE_NAME
from config import SECRET_CHANNEL_TO_NEWS

##Стоп лист для произведений вида: айди: [произведение1, произведение2, произведение3, ...]
stop_list_compositions = {}

##Тоже стоп-лист, только с новостями на сервере
last_news  = {}

##Класс ответственный за контроль диалога (Надстройка над классом Compositions);
Controller = ControlDialog()

##Намерения для корректной работы событий on_member_join, on_member_remove;
intents = discord.Intents.all()
bot = commands.Bot(PREFIX, intents=intents)

##Сработает при запуске бота
@bot.event
async def on_ready():
    ##Меняем статус бота на: Играет в .info | .info доп
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(".info | .info доп"))

    print(f"Бот --{bot.user}-- успешно запущен!")
    await search_news()

##Событие на присоединение к серверу пользователя
@bot.event
async def on_member_join(member: discord.Member):
    ##Формируем название произведения и его текст
    composition_title, composition_text, composition_name = Controller.msg_on_join()

    ##Отсылаем пользователю сообщение в лс
    await member.send(f"{composition_title}\n```{composition_text}```")

##Событие на выход с сервера пользователя
@bot.event
async def on_member_remove(member: discord.User):
    ##Формируем название произведения и его текст
    composition_title, composition_text, composition_name = Controller.msg_on_remove()

    ##Отсылаем пользователю сообщение в лс
    try:
        await member.send(f"{composition_title}\n```{composition_text}```")
    except:
        print(f"---Ошибка---\nНе могу написать в лс пользователю {member}.")

##Событие на любое сообщение
@bot.event
async def on_message(message):

    ##Всё в try-except для того, чтобы пользователь мог писать в ЛС боту.
    try:
        ##Если у гильдии нет стоп-листа - добавляем и присваиваем пустой список
        if message.guild.id not in stop_list_compositions:
            stop_list_compositions[message.guild.id] = []
    except: ##Сработает если пользователь пишет боту в ЛС.
        if message.author.id not in stop_list_compositions:
            stop_list_compositions[message.author.id] = []

    try:
        ##Если айди гильдии нет в ключах последней новости
        if message.guild.id not in last_news:
            last_news[message.guild.id] = []

        if Controller.get_last_new()["title"] not in last_news[message.guild.id]:
            ##Получаем последнюю новость
            new = Controller.get_last_new()

            ##Записываем последнюю новость в список последних
            last_news[message.guild.id].append(new["title"])

            ##Заносим в список уже бывших новостей
            last_news[message.guild.id] = [new["title"]]

            ##Составляем Embed
            embed = discord.Embed(title=new["title"], url=new["post_url"], description=new["content"], colour=discord.Color.gold())
            embed.set_image(url=new["image_url"])
            embed.set_footer(text=new["date_time"])

            ##Берём канал по имени
            try:
                channel = discord.utils.get(message.guild.channels, name=SECRET_CHANNEL_TO_NEWS[0])
            except:
                channel = discord.utils.get(message.guild.channels, name=SECRET_CHANNEL_TO_NEWS[1])
                
            ##Отправляем Embed
            try:
                await channel.send(embed=embed)
            except AttributeError:
                print(f"На сервере \"{message.guild.name}\" нет канала новостного канала.")
    except:
        pass


    ##Для реагирования на команды
    await bot.process_commands(message)

##Отправка стиха в лс
@bot.command()
async def composition_verse_me(ctx):

    ##Отправляем пользователю в лс, поэтому делаем стоп-лист для лс - если его нет - делаем пустой список (пустой стоп-лист)
    if ctx.author.id not in stop_list_compositions:
        stop_list_compositions[ctx.author.id] = []

    ##Формируем название, текст, имя файла
    composition_title, composition_text, file_composition = Controller.find_random_composition(find_verse=True, stop_list=stop_list_compositions[ctx.author.id])

    ##Если есть файл - отсылаем с файлом
    if file_composition[0] != None:
        composition_text = composition_text[0:EMBED_LIMIT-100] + "...\n\n---Полностью см. в файле. (снизу)---\n\n"
        embed = discord.Embed(title=f"{composition_title}", colour=discord.Color.red(), description=f"{composition_text}")
        ctx.author.send(embed=embed)
    else:
        embed = discord.Embed(title=f"{composition_title}", colour=discord.Color.red(), description=f"{composition_text}")
        await ctx.author.send(embed=embed)
    
##Команда с информацией о боте
@bot.command()
async def info(ctx, dop=None):

    ##Если не была запрошена дополнительная информация
    if dop == None:
        emb = discord.Embed(title="Навигация по командам", colour=discord.Color.red())
        emb.add_field(name=f"{PREFIX}composition стих | {PREFIX}composition_verse", value="Случайное стихотворение", inline=False)
        emb.add_field(name=f"{PREFIX}composition поэма | {PREFIX}composition_poem", value="Случайная поэма", inline=False)
        emb.add_field(name=f"{PREFIX}composition пьеса | {PREFIX}composition_piece", value="Случайная пьеса", inline=False)
        emb.add_field(name=f"{PREFIX}composition [-название произведения-]", value="Найти произведение по его названию", inline=False)
        emb.add_field(name=f"{PREFIX}info доп", value="Дополнительные команды")
        #emb.set_thumbnail(url="https://regnum.ru/uploads/pictures/news/2016/05/14/regnum_picture_1463247444520776_normal.jpg")
    else: ##Если была запрошена дополнительная информация
        emb = discord.Embed(title="Навигация по командам", colour=discord.Color.gold())
        emb.add_field(name=f"{PREFIX}clear -n-", value="Очистка чата на -n- сообщений.", inline=False)
        emb.add_field(name=f"{PREFIX}kick -@имя участника- [-причина кика-]", value="Кик участника с сервера.", inline=False)
        emb.add_field(name=f"{PREFIX}ban -@имя участника- [-время бана-] [-причина бана-]", value="Бан участника на сервере", inline=False)
        emb.add_field(name=f"{PREFIX}unban -@имя участника-", value="Разбан участника на сервере.", inline=False)
        emb.add_field(name=f"{PREFIX}roll -min- -max-", value="Случайное число от -min- до -max-", inline=False)
        emb.set_footer(text="Сайт бота: https://... (В разработке).")

    ##Отправляем нашу информацию
    await ctx.send(embed=emb)

##Случайное произведение - пользователь может ввести сам
@bot.command()
async def composition(ctx, *, type_composition=None):

    file_composition = None
    ##Ветка стихов: Если пользователь ничего не указал или указал стихи - ищем по умолчанию стихи
    if type_composition == None or len(re.findall(r"с[дт][ие]х?|verses?", type_composition)) > 0:
        #composition_title, composition_text, file_composition = Controller.find_random_composition(find_verse=True)
        await composition_verse(ctx)
    else: ##Иначе - перебираем все остальные варианты

        ##Ветка поэмы: Если пользователь ввёл поэму
        if len(re.findall(r"п[ао]е?м?а?|poem", type_composition)) > 0:
            await composition_poem(ctx)
        ##Ветка пьесы: Если пользователь ввёл в type_composition 'пьеса'
        elif len(re.findall(r"п[ьъ]?е[сз]?а?|piece", type_composition)) > 0:
            await composition_piece(ctx)
        ##Ветка с введённым пользователем произведением
        else:
            await composition_by_name(ctx=ctx, composition_name_from_user=type_composition)

##Произведение по названию
@bot.command()
async def composition_by_name(ctx, *, composition_name_from_user):

    ##Если пользователь пишет в лс - попадём в ветку от except и вставим стоп-лист от пользователя, а не от сервера
    try:
        composition_title, composition_text, file_composition = Controller.find_composition_by_name(composition_name_from_user, stop_list=stop_list_compositions[ctx.guild.id])
    except:
        composition_title, composition_text, file_composition = Controller.find_composition_by_name(composition_name_from_user, stop_list=stop_list_compositions[ctx.author.id])

    ##Если файл есть - отправляем файл
    if file_composition != None:
        composition_text = composition_text[0:LIMIT-100] + "...\n\n---Далее в файле. (снизу)---\n\n"
        embed = discord.Embed(title=f"{composition_title}", colour=discord.Color.red(), description=f"{composition_text}")
        await ctx.send(embed=embed)
        await ctx.send(file=file_composition)
    else:
        embed = discord.Embed(title=f"{composition_title}", colour=discord.Color.red(), description=f"{composition_text}")
        await ctx.send(embed=embed)

    ##Добавляем произведение в стоп-лист
    stop_list_compositions[ctx.guild.id] = Controller.add_composition_to_stop_list(composition_title, stop_list_compositions[ctx.guild.id])

##Случайное стихотворение
@bot.command()
async def composition_verse(ctx):

    try:
        composition_title, composition_text, file_composition = Controller.find_random_composition(find_verse=True, stop_list=stop_list_compositions[ctx.guild.id])
    except:
        composition_title, composition_text, file_composition = Controller.find_random_composition(find_verse=True, stop_list=stop_list_compositions[ctx.author.id])

    ##В Эмбеде максимум символов - 4096 (4050 в config.py)
    if file_composition[0] != None:
        composition_text = composition_text[0:EMBED_LIMIT-100] + "...\n\n---Полностью см. в файле. (снизу)---\n\n"
        embed = discord.Embed(title=f"{composition_title}", colour=discord.Color.red(), description=f"{composition_text}")
        await ctx.send(embed=embed)
        await ctx.send(file=file_composition[0])
    else:
        embed = discord.Embed(title=f"{composition_title}", colour=discord.Color.red(), description=f"{composition_text}")
        await ctx.send(embed=embed)

    ##Добавляем произведение в стоп-лист
    try:
        stop_list_compositions[ctx.guild.id] = Controller.add_composition_to_stop_list(composition_title, stop_list=stop_list_compositions[ctx.guild.id])
    except: ##Попадём сюда если пользователь пишет боту в ЛС.
        stop_list_compositions[ctx.guild.id] = Controller.add_composition_to_stop_list(composition_title, stop_list=stop_list_compositions[ctx.author.id])


##Случайная поэма
@bot.command()
async def composition_poem(ctx):

    ##Если пользователь пишет в лс - попадём в ветку от except и вставим стоп-лист от пользователя, а не от сервера
    try:
        composition_title, composition_text, file_composition = Controller.find_random_composition(find_poem=True, stop_list=stop_list_compositions[ctx.guild.id])
    except:
        composition_title, composition_text, file_composition = Controller.find_random_composition(find_poem=True, stop_list=stop_list_compositions[ctx.author.id])

    ##Если файл есть - отправляем с файлом
    if file_composition[0] != None:
        composition_text = composition_text[0:EMBED_LIMIT-100] + "...\n\n---Полностью см. в файле. (снизу)---\n\n"
        embed = discord.Embed(title=f"{composition_title}", colour=discord.Color.red(), description=f"{composition_text}")
        await ctx.send(embed=embed)
        await ctx.send(file=file_composition[0])
    else:
        embed = discord.Embed(title=f"{composition_title}", colour=discord.Color.red(), description=f"{composition_text}")
        await ctx.send(embed=embed)

    ##Добавляем произведение в стоп-лист
    try:
        stop_list_compositions[ctx.guild.id] = Controller.add_composition_to_stop_list(composition_title, stop_list=stop_list_compositions[ctx.guild.id])
    except: ##Попадём сюда если пользователь пишет боту в ЛС.
        stop_list_compositions[ctx.guild.id] = Controller.add_composition_to_stop_list(composition_title, stop_list=stop_list_compositions[ctx.author.id])


##Случайная пьеса
@bot.command()
async def composition_piece(ctx):

    ##Если пользователь пишет в лс - попадём в ветку от except и вставим стоп-лист от пользователя, а не от сервера
    try:
        composition_title, composition_text, file_composition = Controller.find_random_composition(find_piece=True, stop_list=stop_list_compositions[ctx.guild.id])
    except:
        composition_title, composition_text, file_composition = Controller.find_random_composition(find_piece=True, stop_list=stop_list_compositions[ctx.author.id])

    ##Если файл есть - отправляем с файлом
    if file_composition[0] != None:
        composition_text = composition_text[0:EMBED_LIMIT-100] + "...\n\n---Полностью см. в файле. (снизу)---\n\n"
        embed = discord.Embed(title=f"{composition_title}", colour=discord.Color.red(), description=f"{composition_text}")
        await ctx.send(embed=embed)
        await ctx.send(file=file_composition[0])
    else:
        embed = discord.Embed(title=f"{composition_title}", colour=discord.Color.red(), description=f"{composition_text}")
        await ctx.send(embed=embed)

    ##Добавляем произведение в стоп-лист
    try:
        stop_list_compositions[ctx.guild.id] = Controller.add_composition_to_stop_list(composition_title, stop_list=stop_list_compositions[ctx.guild.id])
    except: ##Попадём сюда если пользователь пишет боту в ЛС.
        stop_list_compositions[ctx.guild.id] = Controller.add_composition_to_stop_list(composition_title, stop_list=stop_list_compositions[ctx.author.id])


##Очистка чата
@bot.command()
@commands.has_permissions(administrator=True)
async def clear(ctx, how_msg=2):

    MAX = 50 ##Максимум сообщений для очистки

    ##Если пользователь не указал сколько сообщений очистить
    if how_msg == None:
        await ctx.reply(f"Следует указать сколько сообщений подлежит очистке!")
    elif int(how_msg) > MAX:
        await ctx.reply(f"{ctx.author.mention} - максимум для удаления - {MAX} сообщений!")
    else:
        await ctx.channel.purge(limit=int(how_msg))

##Кик участника с сервера
@bot.command()
@commands.has_permissions(administrator=True)
async def kick(ctx, member: discord.Member=None, *, reason=None):

    ##Если пользователь не указал кого банить
    if member == None:
        await ctx.reply(f"{ctx.author.mention} - не указал пользователя для кика.")      
    else:
        ##Если причина не указана
        if reason == None:
            reason = "Не указана."

        ##Кикаем пользователя
        #await member.kick(reason=reason)
        await ctx.guild.kick(member, reason=reason)

        ##Составляем Embed
        embed = discord.Embed(colour=discord.Color.red())
        embed.add_field(name="Что произошло?", value=f"{ctx.author.mention} кикнул с сервера \"{ctx.guild.name}\" пользователя {member.mention}.", inline=False)
        embed.add_field(name="Причина:", value=f"{reason}", inline=False)

        ##Отправляем Embed в чат
        await ctx.send(embed=embed)

##Бан участника на сервере
@bot.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member=None, time_to_ban=None, *, reason=None):

    ##Проверка на админа
    #if not ctx.author.guild_permissions.administrator:
        #await ctx.send(f"{ctx.author.mention} - необходимо обладать правами администратора.")

    #if time_to_ban != None:
        #time_to_ban = re.findall(r"\d[+-*/]+", time_to_ban)
        #if len(time_to_ban) > 0:
            #time_to_ban = int(eval(time_to_ban[0]))
        #else:
            #time_to_ban = None

    ##Если пользователь не указал кого банить
    if member == None:
        await ctx.reply(f"{ctx.author.mention} - не указал пользователя для бана.")
    else:
        ##Если причина не была указана
        if reason == None:
            reason = "Не указана."

        time_to_ban_display = None ##С помощью этой переменной будем уведомлять в embed о длительности бана
        ##Если время бана не указано - бан перманентный
        if time_to_ban == None:
            time_to_ban_display = "неограниченное кол-во времени."
        else:
            ##Если время бана было указано - ставим его в причину
            time_to_ban = eval(time_to_ban) if str(eval(time_to_ban)).isdigit() else "неограниченное кол-во времени"
            time_to_ban_display = f"Время бана - {time_to_ban} секунд."

        ##Баним пользователя
        #await member.ban(reason=reason)
        await ctx.guild.ban(member, reason=reason)

        ##Составляем Embed
        embed = discord.Embed(colour=discord.Color.red())
        embed.add_field(name="Что произошло?", value=f"{ctx.author.mention} забанил на сервере \"{ctx.guild.name}\" пользователя {member.mention}.", inline=False)
        embed.add_field(name="Причина:", value=f"{reason}", inline=False)
        embed.add_field(name="Время бана:", value=f"{time_to_ban_display}", inline=False)

        ##Отправляем Embed в чат
        await ctx.send(embed=embed)

        ##Если время было указано - ждём time_to_ban секунд и разбаниваем
        if time_to_ban != None:
            await asyncio.sleep(time_to_ban)
            await member.unban()

##Разбан участника на сервере
@bot.command()
@commands.has_permissions(administrator=True)
async def unban(ctx, *, member: discord.User=None):

    user_name, user_discriminator = str(member).split("#") ##Нулевой - логин пользователя, первый - его дискриминатор. test#1234
    banned_users = await ctx.guild.bans() ##Список всех забаненных пользователей

    ##Пробегаемся по каждому пользователю в списке забаненных для проверки на совпадение с введённым
    for banned_user in banned_users:

        ##Если в списке забаненных пользователей нашёлся тот, который ввёл пользователь-разбанивающий
        if (banned_user.user.name, banned_user.user.discriminator) == (user_name, user_discriminator):
            await ctx.guild.unban(member)
    
            ##Составляем Embed
            embed = discord.Embed(title="Разбан", description=f"{ctx.author.mention} разбанил {member.mention}.", colour=discord.Color.red())

            ##Отсылаем Embed
            await ctx.send(embed=embed)


##Рандомное число от min до max
@bot.command()
async def roll(ctx, min=None, max=None):
    if min == None:
        await ctx.reply(f"{ctx.author.mention} - не указал число -min- и -max-.")
    elif max == None:
        await ctx.reply(f"{ctx.author.mention} - не указал число -max-.")
    else:
        min = int(min)
        max = int(max)

        ##Если минимальное больше максимального - меняем их местами
        if min > max:
            min, max = max, min


        result = random.randint(int(min), int(max))
        await ctx.reply(f"{ctx.author.mention}, {result}")

##Вывод новостей hoi4
@bot.command()
@commands.has_any_role("Игрок в HOI4")
#@commands.has_role("798939758348468244")
async def new_hoi4(ctx, *, index_new=None):

    await ctx.channel.purge(limit=1)

    with sqlite3.connect("data.db") as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        sql = f"SELECT * FROM game_news" ##Берём последнюю запись
        cursor.execute(sql)

        if not index_new.replace("-", "").replace(".", "").replace(",", "").isdigit():
            await ctx.reply(f"{ctx.author.mention} - указал не числовое значение для новости")
        else:
            news = cursor.fetchall()
            try:
                new = news[abs(int(index_new))]
            except IndexError:
                new = news[-1]

        ##Составляем Embed
        embed = discord.Embed(title=new["title"], url=new["post_url"], description=new["content"], colour=discord.Color.gold())
        embed.set_image(url=new["image_url"])
        embed.set_footer(text=new["date_time"])
        
        await ctx.send(embed=embed)

##Парсинг новостей каждые полчаса
async def search_news():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0"
    }
    url = "https://shazoo.ru/tags/6104/hearts-of-iron-iv"

    while True:
        response = requests.get(url, headers=headers)
        html = BS(response.content, "html.parser")
        items = html.find_all("div", class_="flex flex-col gap-2 py-6 first:pt-0")

        ##Открываем файл с БД
        with sqlite3.connect("data.db") as db:
            cursor = db.cursor()

            ##Создание таблицы
            sql = f"""CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                date_time TEXT,
                title TEXT,
                content TEXT,
                post_url TEXT,
                image_url TEXT
            )"""
            cursor.execute(sql)

            ##Перебор карточек новостей в цикле
            for item in items:
                date_time = item.find("time").text.strip()
                title = item.find("h4", class_="text-lg leading-normal font-bold dark:text-gray-300").find("a").get("title")
                content = item.find("div", class_="break-words").text.strip()
                post_url = item.find("h4", class_="text-lg leading-normal font-bold dark:text-gray-300").find("a").get("href")
                image_url = item.find("a", class_="rounded").find("img", class_="rounded").get("src")

                sql = f"INSERT INTO {TABLE_NAME} (date_time, title, content, post_url, image_url) VALUES (?, ?, ?, ?, ?);"
                cursor.execute(sql, (date_time, title, content, post_url, image_url))

        ##Перерыв между итерациями 30 минут
        await asyncio.sleep(60*30)

##Помещаем функцию поиска новостей в вечный цикл
bot.loop.create_task(search_news())

##Точка входа
if __name__ == "__main__":
    bot.run(TOKEN)