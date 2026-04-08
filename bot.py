import discord
from discord.ext import commands
import os
from db import init_db, get_points, update_points, get_leaderboard

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    init_db()
    print(f"Logged in as {bot.user}")

@bot.command()
async def add(ctx, member: discord.Member, amount: int):
    update_points(str(member.id), amount)
    points = get_points(str(member.id))
    await ctx.send(f"{member.mention} now has {points} points.")

@bot.command()
async def sub(ctx, member: discord.Member, amount: int):
    update_points(str(member.id), -amount)
    points = get_points(str(member.id))
    await ctx.send(f"{member.mention} now has {points} points.")

@bot.command()
async def points(ctx, member: discord.Member = None):
    member = member or ctx.author
    points = get_points(str(member.id))
    await ctx.send(f"{member.mention} has {points} points.")

@bot.command()
async def leaderboard(ctx):
    board = get_leaderboard()
    if not board:
        await ctx.send("No data yet.")
        return

    msg = "**Leaderboard**\n"
    for i, (user_id, score) in enumerate(board, start=1):
        user = await bot.fetch_user(int(user_id))
        msg += f"{i}. {user.name} — {score}\n"

    await ctx.send(msg)

bot.run(os.getenv("DISCORD_TOKEN"))
