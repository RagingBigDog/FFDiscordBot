from dis import dis
import string
from unicodedata import name
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
    user = interaction.user
    for channel in guild.text_channels:
        if channel.name == str(interaction.user.id):
            return await interaction.response.send_message(embed=discord.Embed(title='Failure!', description=f'Channel <#{channel.id}> already created!', color=discord.Color.red()))
        guild = interaction.guild
        user = interaction.user
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            user: discord.PermissionOverwrite(read_messages=True)
    }

        channel = await guild.create_text_channel(str(interaction.user.id), overwrites=overwrites)
        return await interaction.response.send_message(embed=discord.Embed(title='Success!', description=f'Channel <#{channel.id}> created!', color=discord.Color.green()))

@tree.command(name='place_bid', description='place a bid on a player', guild=discord.Object(id=653484637934321674))
async def self(interaction: discord.Interaction, bid: int, player: str):
    name = str(interaction.user.id)
    if name != interaction.channel.name:
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
            
            data_file.close()
            n = 4000
            strings = [string[i:i+n] for i in range(0, len(string), n)]

            for s in strings:
                await interaction.response.send_message(s)

@tree.command(name='delete_bid', description='deletes a bid', guild=discord.Object(id=653484637934321674))
async def self(interaction: discord.Interaction, player: str):
    name = str(interaction.user.id)
    if name != interaction.channel.name:
        await interaction.response.send_message(f'You can\'t run this command outside your private channel')
        raise app_commands.NoPrivateMessage('You can\'t run this command outside a private channel!')
    else:
        with open('data.json', 'r') as data_file:
            data = json.loads(data_file.read() or '{}')
            mdata = data.get(str(interaction.user.id)) or None

            if mdata:
                for pdata in mdata:

                    # print(pdata)
                    if player in pdata:
                        # print(player)
                        print("mdata=", mdata, "pdata=", pdata, "player=", player, "this is stuff")
                        print("mdata type = ", type (mdata))
                        print("player type = ", type (player))
                        print("pdata type = ", type (pdata))
                        pdata = "shammies are cool", "42"
                        print(pdata)
                        # del pdata[player, None]
                        # del pdata["player"]
                        # del pdata["jimmynewtron"]
                        # pdata.pop(player)
                        with open('data.json', 'w') as data_file:
                            data_file.write(json.dumps(data, indent=4))
                            data_file.close()
            else:
                data_file.close()
                return await interaction.response.send_message(f'You have no bids!')

            data_file.close()
            
            await interaction.response.send_message(f'The bid has been deleted')
            
slashBot.run(token)