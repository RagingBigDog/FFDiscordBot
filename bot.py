from dis import dis
import string
from urllib import response
import discord
from discord.ext import commands
from discord import InteractionMessage, app_commands
import os
from dotenv import load_dotenv
import json

load_dotenv()
token = os.getenv('TOKEN')

class abot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.sync = False

    async def on_ready(self):
        await tree.sync(guild=discord.Object(id=653484637934321674))
        self.sync = True
        print('Bot is Online')

slashBot = abot()
tree = app_commands.CommandTree(slashBot)

@tree.command(name='create_channel', description='creates a private channel for the user', guild=discord.Object(id=653484637934321674))
async def self(interaction: discord.Interaction):
    guild = interaction.guild
    user = interaction.user.name
    cat = discord.utils.get(guild.categories, name='Private Channels')
    chan = discord.utils.get(guild.channels, name=user) or None
    for channel in guild.channels:
        if chan == channel:
            print('made it')
            return await interaction.response.send_message(embed=discord.Embed(title='Failure!', description=f'Channel <{channel.id}> already created!', color=discord.Color.red()))
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        user: discord.PermissionOverwrite(read_messages=True)
    }

    channel = await guild.create_text_channel(str(interaction.user.id), overwrites=overwrites, category=cat)
    return await interaction.response.send_message(embed=discord.Embed(title='Success!', description=f'Channel <#{channel.id}> created!', color=discord.Color.green()))

@tree.command(name='place_bid', description='place a bid on a player', guild=discord.Object(id=653484637934321674))
async def self(interaction: discord.Interaction, bid: int, player: str):
    name = str(interaction.user.id)
    if name != interaction.channel.id :
        await interaction.response.send_message(f'You can\'t run this command outside your private channel')
        raise app_commands.NoPrivateMessage('You can\'t run this command outside a private channel!')
    else:
        with open('data.json', 'r') as data_file:
            data = json.loads(data_file.read() or '{}')
            oldamount = 0
            if not str(interaction.user.id) in data:
                data[str(interaction.user.id)] = {player.lower(): bid}
            else:
                oldamount = data[str(interaction.user.id)].get(player.lower()) or 0
                data[str(interaction.user.id)].update({player.lower(): bid})
            data_file.close()
        with open('data.json', 'w') as data_file:
            data_file.write(json.dumps(data, indent=4))
            data_file.close()
        return await interaction.response.send_message(embed=discord.Embed(title='Success!', description=f"Changed your bid of {player} from {oldamount} to {bid}", color=discord.Color.green())) 

@tree.command(name='view_bids', description='view your current bids', guild=discord.Object(id=653484637934321674))
async def self(interaction: discord.Interaction):
    name = str(interaction.user.id)
    string = ''
    if name != interaction.channel.name:
        await interaction.response.send_message(f'You can\'t run this command outside your private channel')
        raise app_commands.NoPrivateMessage('You can\'t run this command outside a private channel!')
    else:
        with open('data.json', 'r') as data_file:
            data = json.loads(data_file.read() or '{}')
            mdata = data.get(str(interaction.user.id)) or None
            if mdata:
                for k in dict(mdata):
                    string += f'`{k}`: `{dict(mdata)[k]}`\n'
            else:
                return await interaction.response.send_message(f'You have no bids!')
            
            n = 4000
            strings = [string[i:i+n] for i in range(0, len(string), n)]

            for s in strings:
                await interaction.response.send_message(s)
    


slashBot.run(token)