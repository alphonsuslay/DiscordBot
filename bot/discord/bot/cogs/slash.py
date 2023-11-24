import discord
from discord.ext import commands
from discord import app_commands
import json


def load_config():
    with open("settings/config.json", 'r') as config_file:
        return json.load(config_file)
    
class Slash(commands.Cog):
    def __init__(self, client : commands.Bot):
        self.client = client
        # Load the suggestion channel ID from the config
        self.suggestion_channel_id = load_config().get("SUGGESTION_CHANNEL_ID")

    @commands.Cog.listener()
    async def on_ready(self):
        print("Slash.py is online")

    @commands.command()
    async def sync(self, ctx) -> None:
        fmt = await ctx.bot.tree.sync(guild = ctx.guild)
        
        await ctx.send(f"Synced {len(fmt)} commands to the server.")

    @app_commands.command(name = "questions", description = "question form")
    async def question(self, interaction: discord.Interaction, question: str):
        await interaction.response.send_message('Answered')

    @app_commands.command(name = "ping", description = "Check the bot's current response time, also known as latency.")
    async def ping(self, interaction: discord.Interaction):
        bot_latency = round(self.client.latency * 100)
        await interaction.response.send_message(f"Bot is running on {bot_latency} ms.")
    
    @app_commands.command(name = "suggest", description = "Submit a suggestion to improve the bot")
    async def suggest(self, interaction: discord.Interaction, suggestion: str):
        if self.suggestion_channel_id:
            # Get the suggestion channel
            suggestion_channel = self.client.get_channel(self.suggestion_channel_id)

            if suggestion_channel:
                # Create an embed for the suggestion
                suggestion_embed = discord.Embed(
                    title="New Suggestion",
                    description=suggestion,
                    color=discord.Color.gold()
                )
                suggestion_embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)

                # Send the suggestion as an embed message to the designated channel
                await suggestion_channel.send(embed=suggestion_embed)

                # Always acknowledge the interaction to prevent "The application did not respond" message
                await interaction.response.send_message("Suggestion submitted successfully.")
            else:
                await interaction.response.send_message("Suggestion channel not found.")
        else:
            await interaction.response.send_message("Suggestion channel is not set. Please use `/suggest_channel` to set it.")

        
    @app_commands.command(name = "suggest_channel", description = "Set the channel where suggestions should be submitted.")
    async def setsuggest(self, interaction: discord.Interaction, channel: discord.TextChannel):
        # Load the existing config or create an empty one if it doesn't exist
        config = load_config()

        # Set the suggestion channel to the provided channel
        config['SUGGESTION_CHANNEL_ID'] = channel.id  # Update the SUGGESTION_CHANNEL_ID in the config

        with open("settings/config.json", 'w') as config_file:
            json.dump(config, config_file, indent=4)  # Save the updated config

        # Check if the channel exists; if not, create it
        suggestion_channel = self.client.get_channel(channel.id)
        if not suggestion_channel:
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True)
            }

            suggestion_channel = await interaction.guild.create_text_channel(
                name="suggestions",
                overwrites=overwrites,
                category=None  # Replace with the category ID if needed
            )

        self.suggestion_channel_id = channel.id  # Update the suggestion channel ID in-memory

        await interaction.response.send_message(f"Suggestions will now be sent to {channel.mention}")

async def setup(client):
    with open("settings/config.json", 'r') as config_file:
        config = json.load(config_file)
    
    server_id = config.get("SERVER_ID")
    
    if server_id is not None:
        await client.add_cog(Slash(client), guilds=[discord.Object(id=server_id)])


