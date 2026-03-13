import discord
from discord.ext import commands
from discord import app_commands
import os, datetime, random

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="*", intents=intents)
tree = bot.tree

# ---------------- EMBED ---------------- #

def emb(title, desc):
    e = discord.Embed(
        title=title,
        description=desc,
        color=0x8A2BE2
    )
    e.set_footer(text="Kairo Bot")
    e.timestamp = datetime.datetime.utcnow()
    return e

# ---------------- READY ---------------- #

@bot.event
async def on_ready():
    await tree.sync()
    print(f"{bot.user} online")

# ---------------- STATS ---------------- #

async def stats_logic(ctx):
    servers = len(bot.guilds)
    users = sum(g.member_count for g in bot.guilds)
    await ctx.send(embed=emb("Bot Stats", f"Servers: {servers}\nUsers: {users}"))

@bot.command()
async def stats(ctx):
    await stats_logic(ctx)

@tree.command(name="stats")
async def stats_slash(i: discord.Interaction):
    servers = len(bot.guilds)
    users = sum(g.member_count for g in bot.guilds)
    await i.response.send_message(embed=emb("Bot Stats", f"Servers: {servers}\nUsers: {users}"))

# ---------------- INVITE ---------------- #

async def invite_logic(ctx):
    link = f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot%20applications.commands"
    await ctx.send(embed=emb("Invite Kairo", f"[Invite Link]({link})"))

@bot.command()
async def invite(ctx):
    await invite_logic(ctx)

@tree.command(name="invite")
async def invite_slash(i: discord.Interaction):
    link = f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot%20applications.commands"
    await i.response.send_message(embed=emb("Invite Kairo", f"[Invite Link]({link})"))

# ---------------- PING ---------------- #

@bot.command()
async def ping(ctx):
    await ctx.send(embed=emb("Pong", f"{round(bot.latency*1000)} ms"))

@tree.command(name="ping")
async def ping_slash(i: discord.Interaction):
    await i.response.send_message(embed=emb("Pong", "Bot working"))

# ---------------- CLEAR ---------------- #

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount:int):
    await ctx.channel.purge(limit=amount)
    await ctx.send(embed=emb("Cleared", f"{amount} messages deleted"), delete_after=5)

@tree.command(name="clear")
async def clear_slash(i: discord.Interaction, amount:int):
    await i.channel.purge(limit=amount)
    await i.response.send_message(embed=emb("Cleared", f"{amount} messages deleted"))

# ---------------- USER INFO ---------------- #

@bot.command()
async def userinfo(ctx, member:discord.Member=None):
    member = member or ctx.author
    e = discord.Embed(title=member.name, color=0x8A2BE2)
    e.set_thumbnail(url=member.avatar.url)
    e.add_field(name="ID", value=member.id)
    e.add_field(name="Joined", value=member.joined_at.date())
    await ctx.send(embed=e)

@tree.command(name="userinfo")
async def userinfo_slash(i:discord.Interaction, member:discord.Member):
    e = discord.Embed(title=member.name, color=0x8A2BE2)
    e.set_thumbnail(url=member.avatar.url)
    await i.response.send_message(embed=e)

# ---------------- FUN COMMANDS ---------------- #

fun_cmds = [
"8ball","coinflip","roll","joke","meme","rate",
"ship","choose","reverse","say","random"
]

@bot.command()
async def coinflip(ctx):
    await ctx.send(embed=emb("Coin Flip", random.choice(["Heads","Tails"])))

@bot.command()
async def roll(ctx):
    await ctx.send(embed=emb("Dice", str(random.randint(1,6))))

# ---------------- TICKET SYSTEM ---------------- #

class TicketView(discord.ui.View):

    @discord.ui.button(label="Open Ticket", style=discord.ButtonStyle.green)
    async def ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild

        category = discord.utils.get(guild.categories, name="Tickets")

        if not category:
            category = await guild.create_category("Tickets")

        channel = await guild.create_text_channel(
            f"ticket-{interaction.user.name}",
            category=category
        )

        await channel.send(embed=emb(
            "Support Ticket",
            f"{interaction.user.mention} support will assist you shortly."
        ))

        await interaction.response.send_message("Ticket created", ephemeral=True)

@bot.command()
async def ticketsetup(ctx):
    await ctx.send(embed=emb("Support Panel","Click button to create ticket"), view=TicketView())

@tree.command(name="ticketsetup")
async def ticketsetup_slash(i:discord.Interaction):
    await i.response.send_message(embed=emb("Support Panel","Click button to create ticket"), view=TicketView())

# ---------------- GIVEAWAY ---------------- #

@bot.command()
async def gstart(ctx, time:int, *, prize):

    e = emb("Giveaway Started", f"Prize: {prize}\nReact with 🎉")

    msg = await ctx.send(embed=e)

    await msg.add_reaction("🎉")

# ---------------- AI CHAT (placeholder) ---------------- #

@bot.command()
async def ai(ctx, *, question):

    await ctx.send(embed=emb(
        "AI Response",
        "AI system placeholder (connect OpenAI API here)"
    ))

# ---------------- HELP ---------------- #

@bot.command()
async def help(ctx):

    e = discord.Embed(
        title="Kairo Commands",
        description="Prefix *",
        color=0x8A2BE2
    )

    e.add_field(name="Utility", value="ping stats invite userinfo")
    e.add_field(name="Moderation", value="clear")
    e.add_field(name="Fun", value="coinflip roll")
    e.add_field(name="Tickets", value="ticketsetup")
    e.add_field(name="Giveaway", value="gstart")

    await ctx.send(embed=e)

@tree.command(name="help")
async def help_slash(i:discord.Interaction):

    e = discord.Embed(
        title="Kairo Commands",
        description="Use * or /",
        color=0x8A2BE2
    )

    e.add_field(name="Main", value="ping stats invite help")

    await i.response.send_message(embed=e)

bot.run(TOKEN)
