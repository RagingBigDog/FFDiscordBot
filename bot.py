import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
token = os.getenv('TOKEN')


@bot.event
async def on_ready():
    print('Bot is live!')

@bot.command()
async def ping(ctx):
    await ctx.reply('pong')

bot.run(token)