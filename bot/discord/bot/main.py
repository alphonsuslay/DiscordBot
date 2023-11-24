import os
import json
import random
import discord
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, MissingPermissions
from itertools import cycle


# Load configurations from files
def load_data():
    with open("settings/config.json", 'r') as config_file:
        config = json.load(config_file)

    with open("settings/command.json", "r") as json_file:
        command_help = json.load(json_file)

    return config, command_help

config, command_help = load_data()
TOKEN = config.get('TOKEN')
PREFIX = config.get('PREFIX')
STATUS = config.get("STATUS")
ACTIVITY = config.get("ACTIVITY")


intents = discord.Intents.all()
intents.members = True
intents.presences = True
client = commands.Bot(command_prefix=PREFIX, intents=intents)

client.remove_command("help") #remove buit in 'help' command 



#client's status configurations
status_options = {
    "online": discord.Status.online,
    "idle": discord.Status.idle,
    "dnd": discord.Status.dnd,
}

activity_types = {
    "playing": discord.ActivityType.playing,
    "listening": discord.ActivityType.listening,
    "watching": discord.ActivityType.watching
}

# Ensure the configured status is valid
presence_status = status_options.get(STATUS, discord.Status.online)
activity_type = activity_types.get(ACTIVITY, discord.ActivityType.playing)



client_status = cycle([".help", "Discord Bot"])
@tasks.loop(seconds=10)
async def presence():
    await client.change_presence(status=presence_status, activity=discord.Activity(type=activity_type, name=next(client_status)))



async def load():
    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            await client.load_extension(f'cogs.{filename[:-3]}')



#Simple Commands for main file
@client.command()
async def ping(ctx):
            bot_latency = round(client.latency * 100)
            await ctx.send(f"Bot is running on {bot_latency} ms.")

@client.command()
async def eightball(ctx, *, question):
    with open("response.txt", "r") as f:
        random_responses = f.readlines()
        response = random.choice(random_responses).strip()  # Strip newline characters
        await ctx.send(response)

@client.command(aliases=["h"])
async def help(ctx, command_name=None):
    if command_name:
        # Check if a specific command is provided

        matching_commands = {cmd: explanation for cmd, explanation in command_help.items() if command_name.lower() in cmd.lower()}

        if matching_commands:
            # If there are matching commands, show their explanations
            embedhelp = discord.Embed(
                title=f"Matching Commands for '{command_name}'",
                color=discord.Color.blue(),
            )
            embedhelp.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar)

            for cmd, explanation in matching_commands.items():
                # Format the matching command name in bold
                embedhelp.add_field(name=f"**{cmd}**", value=explanation, inline=False)

            await ctx.send(embed=embedhelp)
        else:
            await ctx.send("No matching commands found.")
    else:
        # If no specific command is provided, display a list of available commands and their explanations
        embedhelp = discord.Embed(
            title=f"Bot Commands [ {ctx.prefix} ]",  # Include the current bot prefix
            color=discord.Color.blue(),
            timestamp=ctx.message.created_at,
        )
        embedhelp.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar)

        # Add commands and their explanations to the embed
        for command, explanation in command_help.items():
            # Format the command name in bold
            embedhelp.add_field(name=f"**{command}**", value=explanation, inline=False)

        await ctx.send(embed=embedhelp)

@client.command()
async def serverinfo(ctx):
    server_embed = discord.Embed(
        title=f"Information about {ctx.guild.name}",
        description="All public information about this server.",
        color=discord.Color.gold(),
        timestamp=ctx.message.created_at,
    )
    if ctx.guild.icon:
        server_embed.set_thumbnail(url=ctx.guild.icon.url)
    server_embed.add_field(name="Name: ", value=ctx.guild.name, inline=False)
    server_embed.add_field(name="Server ID: ", value=ctx.guild.id, inline=False)
    server_embed.add_field(name="Owner: ", value=ctx.guild.owner, inline=False)
    server_embed.add_field(name="Member Count: ", value=ctx.guild.member_count, inline=False)
    server_embed.add_field(name="Channels: ", value=len(ctx.guild.channels), inline=False)
    server_embed.add_field(name="Role Count: ", value=len(ctx.guild.roles), inline=False)
    server_embed.add_field(name="Rules Channel: ", value=ctx.guild.rules_channel, inline=False)
    server_embed.add_field(name="Booster Count: ", value=ctx.guild.premium_subscription_count, inline=False)
    server_embed.add_field(name="Booster Tier: ", value=ctx.guild.premium_tier, inline=False)
    server_embed.add_field(name="Booster Role: ", value=ctx.guild.premium_subscriber_role, inline=False)
    server_embed.add_field(
        name="Created at: ",
        value=ctx.guild.created_at.strftime("%A, %d. %B %Y @ %H:%M:%S"),
        inline=False,
    )
    server_embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=server_embed)

@client.command()
async def userinfo(ctx, member: discord.Member = None):
    # If no member is tagged, use the author of the command
    if member is None:
        member = ctx.author

    # Create an embed to display user information
    user_embed = discord.Embed(
        title=f"User Info - {member.display_name}",
        color=discord.Color.blue(),
        timestamp=ctx.message.created_at,
    )
    user_embed.set_thumbnail(url=member.avatar.url)
    user_embed.add_field(name="Username:", value=member.name, inline=True)
    user_embed.add_field(name="Discriminator:", value=member.discriminator, inline=True)
    user_embed.add_field(name="User ID:", value=member.id, inline=True)
    user_embed.add_field(name="Nickname:", value=member.nick if member.nick else "N/A", inline=True)
    user_embed.add_field(name="Joined Server:", value=member.joined_at.strftime("%A, %d. %B %Y @ %H:%M:%S"), inline=True)

    # Get the roles of the user and count them
    roles = [role.name for role in member.roles[1:]]  # Exclude the @everyone role
    user_embed.add_field(name="Number of Roles:", value=str(len(roles)), inline=True)
    user_embed.add_field(name="Roles:", value=", ".join(roles) if roles else "N/A", inline=False)

    user_embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=user_embed)

@client.command()
@has_permissions(administrator=True)
async def message(ctx, channel: discord.TextChannel, *, message_content):
    try:
        await channel.send(message_content)
        await ctx.send(f"Message sent to {channel.mention}: {message_content}")
    except discord.Forbidden:
        await ctx.send("I don't have permission to send messages in that channel.")
    except discord.HTTPException:
        await ctx.send("An error occurred while sending the message.")

@client.command()
@has_permissions(administrator=True) 
async def setprefix(ctx, new_prefix: str):
    # Update the prefix in the config.json file
    config['PREFIX'] = new_prefix
    with open("settings/config.json", 'w') as config_file:
        json.dump(config, config_file, indent=4)

    # Update the bot's command prefix
    client.command_prefix = new_prefix

    await ctx.send(f"Bot prefix updated to `{new_prefix}`")

@client.command()
@commands.has_permissions(administrator=True)
async def setstatus(ctx, status: str):
    """
    Set the bot's status.
    
    Usage: .setstatus [online/idle/dnd]
    """
    status = status.lower()
    if status in status_options:
        presence_status = status_options[status]
        await client.change_presence(status=presence_status, activity=discord.Activity(type=activity_type, name=next(client_status)))

        # Update status in config.json
        config['STATUS'] = status
        with open("settings/config.json", 'w') as config_file:
            json.dump(config, config_file, indent=4)

        await ctx.send(f"Bot status updated to {status.capitalize()}.")
    else:
        await ctx.send("Invalid status. Please use 'online', 'idle', or 'dnd'.")

@client.command(aliases = ["purge"])
@commands.has_permissions(manage_messages = True )
async def clear(ctx, count : int):
    await ctx.channel.purge(limit = count + 1)
    
#Event handler for client
@client.event
async def on_ready():
    await client.tree.sync()
    await load()
    await presence.start()
    print("Bot is ready.")

# Custom error handler for handling command errors
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Invalid command. Use `.help` to see the list of available commands.")  # Handle the "command not found" error
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Invalid command usage. Please provide all required arguments.")  # Handle the case where a required argument is missing
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid channel provided. Please mention a valid text channel.")
    elif isinstance(error, MissingPermissions):
        await ctx.send("You don't have the necessary permissions to use this command.")
    else:
        await ctx.send(f"An error occurred: {error}")  # Handle any other errors

@setprefix.error
async def setprefix_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide a new prefix to set.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have the necessary permissions to use this command.")
    else:
        await ctx.send(f"An error occurred: {error}")

@setstatus.error
async def setstatus_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide a status ('online', 'idle', or 'dnd').")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have the necessary permissions to use this command.")
    else:
        await ctx.send(f"An error occurred: {error}")

client.run(TOKEN)
