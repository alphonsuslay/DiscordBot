import discord
from discord.ext import commands
from discord.ui import View, Button
import json

# Define a function to load the config
def load_config():
    with open("settings/config.json", 'r') as config_file:
        return json.load(config_file)

class Autorole(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Automation.py is online")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Load the existing config or create an empty one if it doesn't exist
        try:
            with open("settings/config.json", 'r') as config_file:
                config = json.load(config_file)
        except FileNotFoundError:
            config = {}

        # Get the autorole state from the config or assume it's False if it doesn't exist
        autorole_state = config.get("AUTOROLE_STATE", "false")

        if autorole_state.lower() == "true":
            # Only assign the autorole and send welcome message if autorole state is true
            # Get the role ID from the config or use None if it doesn't exist
            role_id = config.get("AUTOROLE_ID", None)

            if role_id:
                # Get the role object using the role ID
                role = discord.utils.get(member.guild.roles, id=int(role_id))
                if role:
                    await member.add_roles(role)

            # You can also add code here to log when autorole is given

            # Get the entry log channel ID from the config or use None if it doesn't exist
            entry_log_channel_id = config.get("ENTRY_LOG_CHANNEL_ID", None)

            if entry_log_channel_id:
                # Get the entry log channel object using the channel ID
                entry_log_channel = member.guild.get_channel(int(entry_log_channel_id))

                if entry_log_channel:
                    # Create an embedded message for the entry log
                    embed = discord.Embed(
                        title=f"Welcome {member.name} to the server!",
                        description="Please read our rules and enjoy your stay!",
                        color=discord.Color.blue()
                    )
                    # Use member.avatar.url to get the avatar URL
                    embed.set_thumbnail(url=member.avatar.url)
                    embed.add_field(name="User ID", value=member.id, inline=True)

                    # Send the welcome message to the entry log channel
                    await entry_log_channel.send(embed=embed)

    @commands.command(aliases = ["sar"])
    @commands.has_permissions(administrator=True)  # Check for administrator permissions
    async def setautorole(self, ctx, role: discord.Role):
        # This command allows the server owner or members with administrator permissions to set the autorole
        if ctx.author == ctx.guild.owner or ctx.author.guild_permissions.administrator:
            # Check if the command issuer is the server owner or has administrator permissions
            await ctx.send(f"Setting the autorole to {role.name}.")

            # Store the role ID in the config
            role_id = str(role.id)
            config = {}

            # Load the existing config or create an empty one if it doesn't exist
            try:
                with open("settings/config.json", 'r') as config_file:
                    config = json.load(config_file)
            except FileNotFoundError:
                pass

            config["AUTOROLE_ID"] = role_id

            # Set the autorole state to True
            config["AUTOROLE_STATE"] = "True"

            # Save the updated config
            with open("settings/config.json", 'w') as config_file:
                json.dump(config, config_file, indent=4)
        else:
            await ctx.send("Only the server owner or members with administrator permissions can use this command.")

    @commands.command()
    @commands.has_permissions(administrator=True)  # Check for administrator permissions
    async def setwelcome(self, ctx, channel: discord.TextChannel):
        # This command allows the server owner to set the entry log channel
        if ctx.author == ctx.guild.owner or ctx.author.guild_permissions.administrator:
            # Check if the command issuer is the server owner
            # You can add additional checks if needed
            await ctx.send(f"Setting the welcome channel to {channel.mention}.")

            # Store the entry log channel ID in the config
            entry_log_channel_id = str(channel.id)
            config = {}

            # Load the existing config or create an empty one if it doesn't exist
            try:
                with open("settings/config.json", 'r') as config_file:
                    config = json.load(config_file)
            except FileNotFoundError:
                pass

            config["ENTRY_LOG_CHANNEL_ID"] = entry_log_channel_id

            # Save the updated config
            with open("settings/config.json", 'w') as config_file:
                json.dump(config, config_file, indent=4)
        else:
            await ctx.send("Only the server owner can use this command.")

    @commands.command()
    @commands.has_permissions(administrator=True)  # Check for administrator permissions
    async def autorole(self, ctx):
        # This command toggles the autorole state between True and False
        if ctx.author == ctx.guild.owner or ctx.author.guild_permissions.administrator:
            # Check if the command issuer is the server owner or has administrator permissions

            # Load the existing config or create an empty one if it doesn't exist
            try:
                with open("settings/config.json", 'r') as config_file:
                    config = json.load(config_file)
            except FileNotFoundError:
                config = {}

            # Get the current autorole state from the config, default to "False" if it doesn't exist
            autorole_state = config.get("AUTOROLE_STATE", "False")

            # Toggle the autorole state
            if autorole_state == "True":
                config["AUTOROLE_STATE"] = "False"
                await ctx.send("Autorole is now turned off.")
            else:
                config["AUTOROLE_STATE"] = "True"
                await ctx.send("Autorole is now turned on.")

            # Save the updated config
            with open("settings/config.json", 'w') as config_file:
                json.dump(config, config_file, indent=4)
        else:
            await ctx.send("Only the server owner or members with administrator permissions can use this command.")

    @commands.command(aliases = ["cr"])
    @commands.has_permissions(manage_roles=True)
    async def createrole(self, ctx, *, role_name: str):
        try:
            # Create the new role with the specified name
            new_role = await ctx.guild.create_role(name=role_name)

            # Confirmation message
            embed = discord.Embed(
                title="Role Created",
                description=f"Role `{new_role.name}` has been created successfully.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)

        except discord.Forbidden:
            # If the bot doesn't have permission to manage roles
            await ctx.send("I don't have permission to manage roles.")

    @commands.command(aliases = ["rr"])
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx, user: discord.Member, *, role_name: str):
        # Find the role by name
        role_to_remove = discord.utils.get(ctx.guild.roles, name=role_name)

        if role_to_remove:
            if role_to_remove in user.roles:
                # Remove the role from the user
                await user.remove_roles(role_to_remove)

                # Confirmation message
                embed = discord.Embed(
                    title="Role Removed",
                    description=f"Role `{role_to_remove.name}` has been removed from {user.mention}.",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"{user.mention} doesn't have the role `{role_to_remove.name}`.")
        else:
            await ctx.send(f"Role `{role_name}` not found.")

    @commands.command(aliases = ["dr"])
    @commands.has_permissions(manage_roles=True)
    async def deleterole(self, ctx, *, role_name: str):
        # Find the role by name
        role_to_delete = discord.utils.get(ctx.guild.roles, name=role_name)

        if role_to_delete:
            try:
                # Delete the role
                await role_to_delete.delete()
                # Confirmation message
                embed = discord.Embed(
                    title="Role Deleted",
                    description=f"Role `{role_to_delete.name}` has been deleted.",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed)
            except discord.Forbidden:
                await ctx.send("I don't have the necessary permissions to delete roles.")
        else:
            await ctx.send(f"Role `{role_name}` not found.")

    @commands.command(aliases = ["ar"])
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, member: discord.Member, *, role_name: str):
        # Find the role by name
        role_to_add = discord.utils.get(ctx.guild.roles, name=role_name)

        if role_to_add:
            try:
                # Add the role to the member
                await member.add_roles(role_to_add)
                # Confirmation message
                embed = discord.Embed(
                    title="Role Added",
                    description=f"Role `{role_to_add.name}` has been added to {member.mention}.",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed)
            except discord.Forbidden:
                await ctx.send("I don't have the necessary permissions to add roles.")
        else:
            await ctx.send(f"Role `{role_name}` not found.")

async def setup(client):
    await client.add_cog(Autorole(client))
