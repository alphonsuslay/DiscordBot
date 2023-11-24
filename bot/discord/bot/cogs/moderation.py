import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Moderation.py is online")

    @commands.command()
    @commands.has_permissions(kick_members = True)
    async def kick(self, ctx, member: discord.Member, *, modreason):
         await ctx.guild.kick(member)
         Embed_kicked = discord.Embed( color = discord.Colour.dark_grey(), timestamp = ctx.message.created_at)
         Embed_kicked.set_thumbnail(url = ctx.author.avatar)
         Embed_kicked.add_field(name = "**Kicked**", value = f"{member.mention} has been kicked from the server by {ctx.author.mention}.", inline = False)
         Embed_kicked.add_field(name = "**Reason:**", value = modreason, inline = True)
         
         await ctx.send(embed = Embed_kicked)

    @commands.command()
    @commands.has_permissions(ban_members = True)
    async def ban(self, ctx, member: discord.Member, *, modreason):
         await ctx.guild.ban(member)
         Embed_banned = discord.Embed( color = discord.Colour.dark_grey(), timestamp = ctx.message.created_at)
         Embed_banned.add_field(name = "**Banned**", value = f"{member.mention} has been banned from the server by {ctx.author.mention}.", inline = False)
         Embed_banned.add_field(name = "**Reason:**", value = modreason, inline = True)
         
         await ctx.send(embed = Embed_banned)

    @commands.command(name = "uba")
    @commands.guild_only()
    @commands.has_permissions(ban_members = True)
    async def unban(self, ctx, userid): 
        user = discord.Object(id = userid)
        await ctx.guild.unban(user)
        Embed_unbanned = discord.Embed( color = discord.Colour.dark_grey(), timestamp = ctx.message.created_at)
        Embed_unbanned.add_field(name = "**Unbanned**", value = f"<@{userid}> has been unbanned from the server by {ctx.author.mention}.", inline = False)

        await ctx.send(embed = Embed_unbanned)           
        
    
async def setup(client):
    await client.add_cog(Moderation(client))

