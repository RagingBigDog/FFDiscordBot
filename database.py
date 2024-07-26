# database.py

import os
import sqlite3
import asyncio
import aiosqlite
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the data directory and DB_PATH
data_dir = 'data'
DB_PATH = os.path.join(data_dir, 'fml_bot.db')

# Ensure the data directory exists
os.makedirs(data_dir, exist_ok=True)

async def setup_database():
    """Set up the SQLite database and create necessary tables."""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS bids
                (user_id INTEGER, player TEXT, amount INTEGER,
                PRIMARY KEY (user_id, player))
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS faab_balances
                (user_id INTEGER PRIMARY KEY, balance INTEGER)
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS admin_channels
                (channel_type TEXT PRIMARY KEY, channel_id INTEGER)
            ''')
            await db.commit()
            
        logger.info(f"Database setup complete at {DB_PATH}")
    except sqlite3.OperationalError as e:
        logger.error(f"Database error: {e}")
        logger.error(f"Current working directory: {os.getcwd()}")
        logger.error(f"Attempting to create database at: {DB_PATH}")
        raise

async def store_bid(user_id: int, player: str, amount: int):
    """
    Store a bid in the database.

    Args:
        user_id (int): The user's ID.
        player (str): The player being bid on.
        amount (int): The bid amount.
    """
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute('''
                INSERT OR REPLACE INTO bids (user_id, player, amount)
                VALUES (?, ?, ?)
            ''', (user_id, player.lower(), amount))
            await db.commit()
        logger.info(f"Stored bid: user_id={user_id}, player={player}, amount={amount}")
    except Exception as e:
        logger.error(f"Error storing bid: {str(e)}")
        raise

async def get_user_bids(user_id: int):
    """
    Retrieve all bids for a user.

    Args:
        user_id (int): The user's ID.

    Returns:
        list: A list of tuples containing (player, amount) for each bid.
    """
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute('SELECT player, amount FROM bids WHERE user_id = ?', (user_id,)) as cursor:
                bids = await cursor.fetchall()
        logger.info(f"Retrieved bids for user_id={user_id}: {bids}")
        return bids
    except Exception as e:
        logger.error(f"Error retrieving user bids: {str(e)}")
        raise

async def update_faab_balance(user_id: int, new_balance: int):
    """
    Update the FAAB balance for a user.

    Args:
        user_id (int): The user's ID.
        new_balance (int): The new FAAB balance.
    """
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute('''
                INSERT OR REPLACE INTO faab_balances (user_id, balance)
                VALUES (?, ?)
            ''', (user_id, new_balance))
            await db.commit()
        logger.info(f"Updated FAAB balance: user_id={user_id}, new_balance={new_balance}")
    except Exception as e:
        logger.error(f"Error updating FAAB balance: {str(e)}")
        raise

async def get_faab_balance(user_id: int):
    """
    Get the FAAB balance for a user.

    Args:
        user_id (int): The user's ID.

    Returns:
        int or None: The user's FAAB balance, or None if not found.
    """
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute('SELECT balance FROM faab_balances WHERE user_id = ?', (user_id,)) as cursor:
                result = await cursor.fetchone()
        balance = result[0] if result else None
        logger.info(f"Retrieved FAAB balance for user_id={user_id}: {balance}")
        return balance
    except Exception as e:
        logger.error(f"Error retrieving FAAB balance: {str(e)}")
        raise

async def clear_all_bids():
    """Clear all bids from the database."""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute('DELETE FROM bids')
            await db.commit()
        logger.info("Cleared all bids")
    except Exception as e:
        logger.error(f"Error clearing all bids: {str(e)}")
        raise

async def remove_bid(user_id: int, player: str):
    """
    Remove a specific bid for a user.

    Args:
        user_id (int): The user's ID.
        player (str): The player to remove the bid for.
    """
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute('DELETE FROM bids WHERE user_id = ? AND player = ?', (user_id, player.lower()))
            await db.commit()
        logger.info(f"Removed bid: user_id={user_id}, player={player}")
    except Exception as e:
        logger.error(f"Error removing bid: {str(e)}")
        raise

async def get_bid(user_id: int, player: str):
    """
    Get a specific bid for a user.

    Args:
        user_id (int): The user's ID.
        player (str): The player to get the bid for.

    Returns:
        tuple or None: A tuple containing the bid amount, or None if not found.
    """
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute('SELECT amount FROM bids WHERE user_id = ? AND player = ?', (user_id, player.lower())) as cursor:
                result = await cursor.fetchone()
        logger.info(f"Retrieved bid: user_id={user_id}, player={player}, amount={result[0] if result else None}")
        return result
    except Exception as e:
        logger.error(f"Error retrieving bid: {str(e)}")
        raise

async def set_admin_channel(channel_type: str, channel_id: int):
    """
    Set an admin channel.

    Args:
        channel_type (str): The type of admin channel (e.g., 'faab', 'admin_log').
        channel_id (int): The ID of the channel to set.
    """
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute('''
                INSERT OR REPLACE INTO admin_channels (channel_type, channel_id)
                VALUES (?, ?)
            ''', (channel_type, channel_id))
            await db.commit()
        logger.info(f"Set admin channel: type={channel_type}, id={channel_id}")
    except Exception as e:
        logger.error(f"Error setting admin channel: {str(e)}")
        raise

async def get_admin_channel(channel_type: str):
    """
    Get an admin channel ID.

    Args:
        channel_type (str): The type of admin channel to retrieve.

    Returns:
        int or None: The channel ID, or None if not found.
    """
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute('SELECT channel_id FROM admin_channels WHERE channel_type = ?', (channel_type,)) as cursor:
                result = await cursor.fetchone()
        channel_id = result[0] if result else None
        logger.info(f"Retrieved admin channel: type={channel_type}, id={channel_id}")
        return channel_id
    except Exception as e:
        logger.error(f"Error retrieving admin channel: {str(e)}")
        raise