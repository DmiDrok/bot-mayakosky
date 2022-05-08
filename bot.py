import discord
from discord.ext import commands
from config import TOKEN, PREFIX
from config import LIMIT
from config import all_compositions_verses, all_compositions_poems, all_compositions_pieces
import asyncio
import re
from classes.control_dialog_output import ControlDialog

Controller = ControlDialog()

intents = discord.Intents.all()
bot = commands.Bot(PREFIX, intents=intents)

##Сработает при запуске бота
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(".info | .info доп"))
    print(f"Бот --{bot.user}-- успешно запущен!")

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

##Отправка стиха в лс
@bot.command()
async def composition_verse_me(ctx):
    composition_title, composition_text, composition_name, file_composition = Controller.find_random_verse()

    if file_composition != None:
        await ctx.author.send(f"{composition_title}", file=file_composition)
    else:
        await ctx.author.send(f"{composition_title}\n```{composition_text}```")
    
##Команда с информацией о боте
@bot.command()
async def info(ctx, dop=None):

    if dop == None:
        emb = discord.Embed(title="Навигация по командам", colour=discord.Color.red())
        emb.add_field(name=f"{PREFIX}composition стих | {PREFIX}composition_verse", value="Случайное стихотворение", inline=False)
        emb.add_field(name=f"{PREFIX}composition поэма | {PREFIX}composition_poem", value="Случайная поэма", inline=False)
        emb.add_field(name=f"{PREFIX}composition пьеса | {PREFIX}composition_piece", value="Случайная пьеса", inline=False)
        emb.add_field(name=f"{PREFIX}info доп", value="Дополнительные команды")
        #emb.set_thumbnail(url="https://regnum.ru/uploads/pictures/news/2016/05/14/regnum_picture_1463247444520776_normal.jpg")
    else:
        emb = discord.Embed(title="Навигация по командам", colour=discord.Color.gold())
        emb.add_field(name=f"{PREFIX}clear -n-", value="Очистка чата на -n- сообщений.", inline=False)
        emb.add_field(name=f"{PREFIX}kick -@имя участника- [-причина кика-]", value="Кик участника с сервера.", inline=False)
        emb.add_field(name=f"{PREFIX}ban -@имя участника- [-время бана-] [-причина бана-]", value="Бан участника на сервере", inline=False)
        emb.add_field(name=f"{PREFIX}unban -@имя участника-", value="Разбан участника на сервере.")
        emb.set_footer(text="Сайт с подобными ботами: https://ru-poets-discord/")

    await ctx.send(embed=emb)


##Случайное произведение - пользователь может ввести сам
@bot.command()
async def composition(ctx, type_composition=None):

    file_composition = None
    ##Ветка стихов: Если пользователь ничего не указал или указал стихи - ищем по умолчанию стихи
    if type_composition == None or len(re.findall(r"с[дт]?[ие]х?", type_composition)) > 0:
        composition_title, composition_text, composition_name, file_composition = Controller.find_random_verse()
    else: ##Иначе - перебираем все остальные варианты
        ##Ветка поэмы: Если пользователь ввёл поэму
        if len(re.findall(r"п[ао]е?м?а?", type_composition)) > 0:
            composition_title, composition_text, composition_name, file_composition = Controller.find_random_poem()
        ##Ветка пьесы: Если пользователь ввёл в type_composition 'пьеса'
        elif len(re.findall(r"п[ьъ]?е[сз]?а", type_composition)) > 0:
            composition_title, composition_text, composition_name, file_composition = Controller.find_random_piece()

    ##Если файла есть - отправляем с файлом
    if file_composition != None:
        #file_composition = discord.File(file_composition)
        await ctx.send(f"{composition_title}", file=file_composition)
    else:
        await ctx.send(f"{composition_title}\n```{composition_text}```")

##Случайное стихотворение
@bot.command()
async def composition_verse(ctx):
    composition_title, composition_text, composition_name, file_composition = Controller.find_random_verse()

    ##Если файл есть - отправляем с файлом
    if file_composition != None:
        await ctx.send(f"{composition_title}", file=file_composition)
    else:
        await ctx.send(f"{composition_title}\n```{composition_text}```")

##Случайная поэма
@bot.command()
async def composition_poem(ctx):
    composition_title, composition_text, composition_name, file_composition = Controller.find_random_poem()

    ##Если файл есть - отправляем с файлом
    if file_composition != None:
        await ctx.send(f"{composition_title}", file=file_composition)
    else:
        await ctx.send(f"{composition_title}\n```{composition_text}```")

##Случайная пьеса
@bot.command()
async def composition_piece(ctx):
    composition_title, composition_text, composition_name, file_composition = Controller.find_random_piece()

    ##Если файл есть - отправляем с файлом
    if file_composition != None:
        await ctx.send(f"{composition_title}", file=file_composition)
    else:
        await ctx.send(f"{composition_title}\n```{composition_text}```")

##Очистка чата
@bot.command()
@commands.has_permissions(administrator=True)
async def clear(ctx, how_msg=2):

    ##Если пользователь не указал сколько сообщений очистить
    if how_msg == None:
        await ctx.reply(f"Следует указать сколько сообщений подлежит очистке!")
    elif int(how_msg) > 10:
        await ctx.reply(f"{ctx.author.mention} - максимум для удаления - 10 сообщений!")
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
        await member.kick(reason=reason)

        ##Составляем Embed
        embed = discord.Embed(title="Кого-то хлопнули.", colour=discord.Color.red())
        embed.add_field(name="Что случилось?", value=f"{ctx.author.mention} кикнул с сервера \"{ctx.guild.name}\" пользователя {member.mention}.", inline=False)
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

    if time_to_ban != None:
        time_to_ban = int(re.findall(r"\d+", time_to_ban)[0]) if len(int(re.findall(r"\d+", time_to_ban)[0])) > 0 else None

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
            time_to_ban_display = "Время бана - неограниченное кол-во времени."
        else:
            ##Если время бана было указано - ставим его в причину
            time_to_ban = int(time_to_ban) if time_to_ban.isdigit() else "неограниченное кол-во времени"
            time_to_ban_display = f"Время бана - {time_to_ban} секунд."

        ##Баним пользователя
        await member.ban(reason=reason)

        ##Составляем Embed
        embed = discord.Embed(title="Кого-то хлопнули.", colour=discord.Color.red())
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

if __name__ == "__main__":
    bot.run(TOKEN)