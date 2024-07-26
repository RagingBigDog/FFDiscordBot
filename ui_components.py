# ui_components.py

import discord
import logging

logger = logging.getLogger(__name__)

class BidConfirmation(discord.ui.View):
    def __init__(self, *, timeout=30):
        super().__init__(timeout=timeout)
        self.value = None

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Confirm the bid."""
        self.value = True
        self.stop()
        await interaction.response.defer()
        logger.info(f"User {interaction.user.id} confirmed bid")

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Cancel the bid."""
        self.value = False
        self.stop()
        await interaction.response.defer()
        logger.info(f"User {interaction.user.id} cancelled bid")

class BidManagement(discord.ui.View):
    def __init__(self, cog, user_id, *, timeout=60):
        super().__init__(timeout=timeout)
        self.cog = cog
        self.user_id = user_id

    @discord.ui.button(label="View Bids", style=discord.ButtonStyle.blurple)
    async def view_bids(self, interaction: discord.Interaction, button: discord.ui.Button):
        """View current bids."""
        try:
            await interaction.response.defer(ephemeral=True)
            await self.cog.view_bids_internal(interaction, self.user_id)
            logger.info(f"User {self.user_id} viewed their bids")
        except Exception as e:
            logger.error(f"Error viewing bids for user {self.user_id}: {str(e)}")
            await interaction.followup.send("An error occurred while viewing your bids. Please try again later.", ephemeral=True)

    @discord.ui.button(label="Modify Bid", style=discord.ButtonStyle.gray)
    async def modify_bid(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Open modal to modify a bid."""
        try:
            modal = ModifyBidModal(self.cog, self.user_id)
            await interaction.response.send_modal(modal)
            logger.info(f"User {self.user_id} opened modify bid modal")
        except Exception as e:
            logger.error(f"Error opening modify bid modal for user {self.user_id}: {str(e)}")
            await interaction.response.send_message("An error occurred while opening the modify bid form. Please try again later.", ephemeral=True)

    @discord.ui.button(label="Remove Bid", style=discord.ButtonStyle.red)
    async def remove_bid(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Open view to remove a bid."""
        try:
            bids = await self.cog.get_user_bids(self.user_id)
            if not bids:
                await interaction.response.send_message("You don't have any active bids to remove.", ephemeral=True)
                return
            view = RemoveBidView(self.cog, self.user_id, bids)
            await interaction.response.send_message("Select a bid to remove:", view=view, ephemeral=True)
            logger.info(f"User {self.user_id} opened remove bid view")
        except Exception as e:
            logger.error(f"Error opening remove bid view for user {self.user_id}: {str(e)}")
            await interaction.response.send_message("An error occurred while opening the remove bid options. Please try again later.", ephemeral=True)

class RemoveBidView(discord.ui.View):
    def __init__(self, cog, user_id, bids):
        super().__init__()
        self.cog = cog
        self.user_id = user_id
        self.add_item(RemoveBidSelect(bids))

class RemoveBidSelect(discord.ui.Select):
    def __init__(self, bids):
        options = [discord.SelectOption(label=f"{player} - {amount}", value=player) for player, amount in bids]
        super().__init__(placeholder="Select a bid to remove", options=options)

    async def callback(self, interaction: discord.Interaction):
        await self.view.cog.remove_bid_internal(interaction, self.view.user_id, self.values[0])

class ModifyBidModal(discord.ui.Modal, title="Modify Bid"):
    def __init__(self, cog, user_id):
        super().__init__()
        self.cog = cog
        self.user_id = user_id

    player = discord.ui.TextInput(label="Player Name", placeholder="Enter the player's name")
    new_amount = discord.ui.TextInput(label="New Bid Amount", placeholder="Enter the new bid amount")

    async def on_submit(self, interaction: discord.Interaction):
        """Handle the submission of the modify bid modal."""
        try:
            await interaction.response.defer(ephemeral=True)
            player_name = self.player.value.strip()
            new_amount = int(self.new_amount.value)
            
            if not player_name:
                await interaction.followup.send("Player name cannot be empty.", ephemeral=True)
                return
            
            if new_amount <= 0:
                await interaction.followup.send("Bid amount must be positive.", ephemeral=True)
                return

            await self.cog.modify_bid_internal(interaction, self.user_id, player_name, new_amount)
            logger.info(f"User {self.user_id} submitted bid modification for {player_name}")
        except ValueError:
            await interaction.followup.send("Invalid bid amount. Please enter a valid number.", ephemeral=True)
        except Exception as e:
            logger.error(f"Error processing bid modification for user {self.user_id}: {str(e)}")
            await interaction.followup.send("An error occurred while modifying your bid. Please try again later.", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        """Handle errors in the modal."""
        logger.error(f"Error in ModifyBidModal for user {self.user_id}: {str(error)}")
        await interaction.followup.send("Oops! Something went wrong. Please try again later.", ephemeral=True)