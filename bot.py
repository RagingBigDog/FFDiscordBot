from dis import disco
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import json

load_dotenv()
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
    author = ctx.author
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        author: discord.PermissionOverwrite(read_messages=True)
    }

    channel = await ctx.guild.create_text_channel(str(ctx.author.id), overwrites=overwrites)
    return await ctx.send(embed=discord.Embed(title='Success!', description=f'Channel <#{channel.id}> created!', color=discord.Color.green()))

@bot.command()
async def bid(ctx, amount:int, *, player:str):
    name = str(ctx.author.id)
    if name in ctx.guild.text_channels:
        await ctx.message.delete()
        raise commands.PrivateMessageOnly('You can\'t run this command outside a private channel The command you typed is being deleted for secrecy')
    with open('data.json', 'r') as data_file:
        data = json.loads(data_file.read() or '{}')
        oldamount = 0
        if not str(ctx.author.id) in data:
            data[str(ctx.author.id)] = {player.lower(): amount}
        else:
            oldamount = data[str(ctx.author.id)].get(player.lower()) or 0
            data[str(ctx.author.id)].update({player.lower(): amount})
        data_file.close()
    with open('data.json', 'w') as data_file:
        data_file.write(json.dumps(data, indent=4))
        data_file.close()
    return await ctx.send(embed=discord.Embed(title='Success!', description=f"Changed your bid of {player} from {oldamount} to {amount}", color=discord.Color.green()))

bot.run(token)