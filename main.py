# main.py

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from database import setup_database
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='bot.log'
)
logger = logging.getLogger(__name__)

data_dir = 'data'
DB_PATH = os.path.join(data_dir, 'fml_bot.db')

# Ensure the data directory exists
os.makedirs(data_dir, exist_ok=True)

load_dotenv()
TOKEN = os.getenv('TOKEN')

class FreeMarketBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        if not os.path.exists(DB_PATH):
            logger.info(f"Database file not found at {DB_PATH}. Creating new database.")
        await setup_database()
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    logger.info(f"Loaded extension: {filename[:-3]}")
                except Exception as e:
                    logger.error(f"Failed to load extension {filename[:-3]}: {str(e)}")

    async def on_ready(self):
        logger.info(f'{self.user} has connected to Discord!')
        await self.tree.sync()

bot = FreeMarketBot()

if __name__ == '__main__':
    try:
        bot.run(TOKEN)
    except Exception as e:
        logger.critical(f"Bot failed to start: {str(e)}")