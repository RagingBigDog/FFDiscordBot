import discord
import os
import random
from dotenv import load_dotenv

client = discord.Client()
token = os.getenv('TOKEN')

@client.event
async def on_ready():
    print('Logged in as a bot {0.user}'.format(client))

@client.event
async def on_message(message):
    username = str(message.author).split('#')[0]
    channel = str(message.channel.name)
    user_messsage = str(message.content)

    print(f'Message {user_messsage} by {username} on {channel}')

    if message.author == client.user:
        return
    
    if channel == 'random':
        if user_messsage.lower() == 'hello' or user_messsage.lower() == 'hi':
            await message.channel.send(f'Hello {username}')
            return
        elif user_messsage.lower() == 'bye':
            await message.channel.send(f'Bye {username}')
        elif user_messsage.lower() == 'tell me a joke':
            jokes = [' Can someone please shed more\
                light on how my lamp got stolen?', 
                'Why is she calle Ilene? She \
                stands on equal legs.', 'What do you call a gazelle in a \
                lions terriorty? Denzel.']
            await message.channel.send(random.choice(jokes))