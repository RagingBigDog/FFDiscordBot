# bidding.py

import discord
from discord import app_commands
from discord.ext import commands
from database import store_bid, get_user_bids, update_faab_balance, get_faab_balance, remove_bid, get_bid
from ui_components import BidConfirmation, BidManagement, ModifyBidModal
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Bidding(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='bid', description='Place a bid on a player')
    async def bid(self, interaction: discord.Interaction, amount: int, player: str):
        """
        Place a bid on a player.

        Args:
            interaction (discord.Interaction): The interaction object.
            amount (int): The amount of FAAB to bid.
            player (str): The name of the player to bid on.
        """
        user_id = interaction.user.id

        # Input validation
        if amount <= 0:
            await interaction.response.send_message("Bid amount must be positive.", ephemeral=True)
            return

        if not player.strip():
            await interaction.response.send_message("Player name cannot be empty.", ephemeral=True)
            return

        try:
            current_balance = await get_faab_balance(user_id)
            
            if current_balance is None:
                await interaction.response.send_message("Your FAAB balance hasn't been set. Please contact an admin.", ephemeral=True)
                return
            
            if amount > current_balance:
                await interaction.response.send_message(f"Insufficient FAAB. Your current balance is {current_balance}.", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="Bid Confirmation",
                description=f"Are you sure you want to bid {amount} on {player}?\nYour balance will be {current_balance - amount} after this bid.",
                color=discord.Color.blue()
            )
            
            view = BidConfirmation()
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
            await view.wait()
            
            if view.value is None:
                await interaction.followup.send("Bid cancelled due to timeout.", ephemeral=True)
            elif view.value:
                await self.process_bid(interaction, user_id, player, amount, current_balance)
            else:
                await interaction.followup.send("Bid cancelled.", ephemeral=True)

        except Exception as e:
            logger.error(f"Error in bid command: {str(e)}")
            await interaction.followup.send("An error occurred while processing your bid. Please try again later.", ephemeral=True)

    async def process_bid(self, interaction: discord.Interaction, user_id: int, player: str, amount: int, current_balance: int):
        """
        Process a confirmed bid.

        Args:
            interaction (discord.Interaction): The interaction object.
            user_id (int): The user's ID.
            player (str): The player being bid on.
            amount (int): The bid amount.
            current_balance (int): The user's current FAAB balance.
        """
        try:
            await store_bid(user_id, player, amount)
            new_balance = current_balance - amount
            await update_faab_balance(user_id, new_balance)
            embed = discord.Embed(
                title="Bid Placed",
                description=f"Your bid of {amount} on {player} has been recorded. Your new FAAB balance is {new_balance}.",
                color=discord.Color.green()
            )
            view = BidManagement(self, user_id)
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            logger.info(f"User {user_id} placed a bid of {amount} on {player}")
        except Exception as e:
            logger.error(f"Error processing bid: {str(e)}")
            await interaction.followup.send("An error occurred while processing your bid. Please try again later.", ephemeral=True)

    @app_commands.command(name='view_bids', description='View your current bids')
    async def view_bids(self, interaction: discord.Interaction):
        """
        View the user's current bids.

        Args:
            interaction (discord.Interaction): The interaction object.
        """
        await self.view_bids_internal(interaction, interaction.user.id)

    async def view_bids_internal(self, interaction: discord.Interaction, user_id: int):
        """
        Internal method to view bids for a user.

        Args:
            interaction (discord.Interaction): The interaction object.
            user_id (int): The user's ID.
        """
        try:
            bids = await get_user_bids(user_id)
            
            if not bids:
                embed = discord.Embed(title="Your Bids", description="You haven't placed any bids yet.", color=discord.Color.blue())
            else:
                embed = discord.Embed(title="Your Bids", color=discord.Color.blue())
                for player, amount in bids:
                    embed.add_field(name=player, value=f"Bid: {amount}", inline=False)
            
            balance = await get_faab_balance(user_id)
            embed.add_field(name="FAAB Balance", value=str(balance), inline=False)
            
            view = BidManagement(self, user_id)
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            logger.info(f"User {user_id} viewed their bids")
        except Exception as e:
            logger.error(f"Error viewing bids: {str(e)}")
            await interaction.followup.send("An error occurred while retrieving your bids. Please try again later.", ephemeral=True)

    @app_commands.command(name='modify_bid', description='Modify an existing bid')
    async def modify_bid(self, interaction: discord.Interaction):
        """
        Modify an existing bid.

        Args:
            interaction (discord.Interaction): The interaction object.
        """
        modal = ModifyBidModal(self, interaction.user.id)
        await interaction.response.send_modal(modal)

    async def modify_bid_internal(self, interaction: discord.Interaction, user_id: int, player: str, new_amount: int):
        """
        Internal method to modify a bid.

        Args:
            interaction (discord.Interaction): The interaction object.
            user_id (int): The user's ID.
            player (str): The player whose bid is being modified.
            new_amount (int): The new bid amount.
        """
        try:
            current_bid = await get_bid(user_id, player)
            
            if not current_bid:
                await interaction.followup.send(f"You don't have an active bid on {player}.", ephemeral=True)
                return
            
            current_balance = await get_faab_balance(user_id)
            balance_difference = new_amount - current_bid[0]
            
            if balance_difference > current_balance:
                await interaction.followup.send(f"Insufficient FAAB. Your current balance is {current_balance}.", ephemeral=True)
                return
            
            await store_bid(user_id, player, new_amount)
            new_balance = current_balance - balance_difference
            await update_faab_balance(user_id, new_balance)
            
            embed = discord.Embed(
                title="Bid Modified",
                description=f"Your bid on {player} has been updated to {new_amount}. Your new FAAB balance is {new_balance}.",
                color=discord.Color.green()
            )
            view = BidManagement(self, user_id)
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            logger.info(f"User {user_id} modified their bid on {player} to {new_amount}")
        except Exception as e:
            logger.error(f"Error modifying bid: {str(e)}")
            await interaction.followup.send("An error occurred while modifying your bid. Please try again later.", ephemeral=True)

    async def remove_bid_internal(self, interaction: discord.Interaction, user_id: int, player: str):
        """
        Internal method to remove a bid.

        Args:
            interaction (discord.Interaction): The interaction object.
            user_id (int): The user's ID.
            player (str): The player whose bid is being removed.
        """
        try:
            current_bid = await get_bid(user_id, player)
            
            if not current_bid:
                await interaction.response.send_message(f"You don't have an active bid on {player}.", ephemeral=True)
                return
            
            current_balance = await get_faab_balance(user_id)
            new_balance = current_balance + current_bid[0]
            
            await remove_bid(user_id, player)
            await update_faab_balance(user_id, new_balance)
            
            embed = discord.Embed(
                title="Bid Removed",
                description=f"Your bid on {player} has been removed. Your new FAAB balance is {new_balance}.",
                color=discord.Color.green()
            )
            view = BidManagement(self, user_id)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            logger.info(f"User {user_id} removed their bid on {player}")
        except Exception as e:
            logger.error(f"Error removing bid: {str(e)}")
            await interaction.response.send_message("An error occurred while removing your bid. Please try again later.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Bidding(bot))