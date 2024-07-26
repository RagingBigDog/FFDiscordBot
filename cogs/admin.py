# cogs/admin.py

import discord
from discord import app_commands
from discord.ext import commands
from database import update_faab_balance, set_admin_channel, get_admin_channel
import logging

logger = logging.getLogger(__name__)

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.faab_channel_id = None
        self.admin_log_channel_id = None

    async def cog_load(self):
        """Initialize admin channels on cog load."""
        try:
            self.faab_channel_id = await get_admin_channel('faab')
            self.admin_log_channel_id = await get_admin_channel('admin_log')
            logger.info("Admin channels initialized")
        except Exception as e:
            logger.error(f"Error initializing admin channels: {str(e)}")

    @app_commands.command(name='set_faab', description='Set FAAB balance for a user')
    @app_commands.checks.has_permissions(administrator=True)
    async def set_faab(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        """
        Set FAAB balance for a user.

        Args:
            interaction (discord.Interaction): The interaction object.
            user (discord.Member): The user to set FAAB for.
            amount (int): The new FAAB amount.
        """
        if amount < 0:
            await interaction.response.send_message("FAAB amount cannot be negative.", ephemeral=True)
            return

        try:
            await update_faab_balance(user.id, amount)
            await interaction.response.send_message(f"FAAB balance for {user.display_name} has been set to {amount}.", ephemeral=True)
            
            if self.faab_channel_id:
                channel = self.bot.get_channel(self.faab_channel_id)
                if channel:
                    await channel.send(f"FAAB balance update: {user.display_name} now has {amount} FAAB.")
            
            if self.admin_log_channel_id:
                log_channel = self.bot.get_channel(self.admin_log_channel_id)
                if log_channel:
                    await log_channel.send(f"Admin {interaction.user.display_name} set FAAB balance for {user.display_name} to {amount}.")
            
            logger.info(f"FAAB balance set for user {user.id} to {amount} by admin {interaction.user.id}")
        except Exception as e:
            logger.error(f"Error setting FAAB balance: {str(e)}")
            await interaction.response.send_message("An error occurred while setting FAAB balance. Please try again later.", ephemeral=True)

    @app_commands.command(name='set_faab_channel', description='Set the channel for FAAB updates')
    @app_commands.checks.has_permissions(administrator=True)
    async def set_faab_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """
        Set the channel for FAAB updates.

        Args:
            interaction (discord.Interaction): The interaction object.
            channel (discord.TextChannel): The channel to set for FAAB updates.
        """
        try:
            self.faab_channel_id = channel.id
            await set_admin_channel('faab', channel.id)
            await interaction.response.send_message(f"FAAB update channel has been set to {channel.mention}.", ephemeral=True)
            
            if self.admin_log_channel_id:
                log_channel = self.bot.get_channel(self.admin_log_channel_id)
                if log_channel:
                    await log_channel.send(f"Admin {interaction.user.display_name} set FAAB update channel to {channel.mention}.")
            
            logger.info(f"FAAB update channel set to {channel.id} by admin {interaction.user.id}")
        except Exception as e:
            logger.error(f"Error setting FAAB channel: {str(e)}")
            await interaction.response.send_message("An error occurred while setting the FAAB channel. Please try again later.", ephemeral=True)

    @app_commands.command(name='set_admin_log_channel', description='Set the channel for admin action logs')
    @app_commands.checks.has_permissions(administrator=True)
    async def set_admin_log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """
        Set the channel for admin action logs.

        Args:
            interaction (discord.Interaction): The interaction object.
            channel (discord.TextChannel): The channel to set for admin logs.
        """
        try:
            self.admin_log_channel_id = channel.id
            await set_admin_channel('admin_log', channel.id)
            await interaction.response.send_message(f"Admin log channel has been set to {channel.mention}.", ephemeral=True)
            await channel.send(f"This channel has been set as the admin log channel by {interaction.user.display_name}.")
            logger.info(f"Admin log channel set to {channel.id} by admin {interaction.user.id}")
        except Exception as e:
            logger.error(f"Error setting admin log channel: {str(e)}")
            await interaction.response.send_message("An error occurred while setting the admin log channel. Please try again later.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Admin(bot))