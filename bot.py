from urllib import response
import discord
from discord.ext import commands
from discord import app_commands
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
    if name in interaction.guild.text_channels:
        raise commands.PrivateMessageOnly('You can\'t run this command outside a private channel!')
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

slashBot.run(token)