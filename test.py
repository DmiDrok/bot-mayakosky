import discord
from discord.ext import commands

#intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".")

@bot.command()
async def kick(ctx, member):
	await member.kick(reason="0")

bot.run("OTcxODUxNzQ2NDMzNDUwMDY0.G5tiHi.GdAsGi7ZvDRLIoJK5c9mesB1hdw5XEsuJQu__g")