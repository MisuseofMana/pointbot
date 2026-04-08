import discord
from discord import app_commands
from discord.ext import commands
import os
from db import init_db, get_points, update_points, get_leaderboard

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree  # slash command tree

@bot.event
async def on_ready():
    init_db()
    await tree.sync()  # sync slash commands to Discord
    print(f"Logged in as {bot.user}")

# /add
@tree.command(name="add", description="Add points to a user")
@app_commands.describe(member="User to give points to", amount="Amount of points")
async def add(interaction: discord.Interaction, member: discord.Member, amount: int):
    new_score = update_points(str(member.id), amount)
    await interaction.response.send_message(
        f"{member.mention} now has {new_score} points."
    )

# /sub
@tree.command(name="sub", description="Subtract points from a user")
@app_commands.describe(member="User to subtract points from", amount="Amount of points")
async def sub(interaction: discord.Interaction, member: discord.Member, amount: int):
    new_score = update_points(str(member.id), -amount)
    await interaction.response.send_message(
        f"{member.mention} now has {new_score} points."
    )

# /points
@tree.command(name="points", description="Check points")
@app_commands.describe(member="User to check (optional)")
async def points(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    pts = get_points(str(member.id))
    await interaction.response.send_message(
        f"{member.mention} has {pts} points."
    )

# /leaderboard
@tree.command(name="leaderboard", description="Show top users")
async def leaderboard(interaction: discord.Interaction):
    board = get_leaderboard()

    if not board:
        await interaction.response.send_message("No data yet.")
        return

    msg = "**Leaderboard**\n"
    for i, (user_id, score) in enumerate(board, start=1):
        user = await bot.fetch_user(int(user_id))
        msg += f"{i}. {user.name} — {score}\n"

    await interaction.response.send_message(msg)

bot.run(os.getenv("DISCORD_TOKEN"))
