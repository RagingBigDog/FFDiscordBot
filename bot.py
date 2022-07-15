from dis import disco
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
async def create_channel(ctx):
    for channel in ctx.guild.text_channels:
        if channel.name == str(ctx.author.id):
            return await ctx.send(embed=discord.Embed(title='Failure!', description=f'Channel <#{channel.id}> already created!', color=discord.Color.red()))
    guild = ctx.guild
    member = ctx.author
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        member: discord.PermissionOverwrite(read_messages=True)
    }

    channel = await ctx.guild.create_text_channel(str(ctx.author.id), overwrites=overwrites)
    return await ctx.send(embed=discord.Embed(title='Success!', description=f'Channel <#{channel.id}> created!', color=discord.Color.green()))

bot.run(token)