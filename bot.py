import os
import sqlite3
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
DB_PATH = os.getenv("DB_PATH", "points.sqlite")

# Connect to SQLite
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS points (
    user_id TEXT PRIMARY KEY,
    points INTEGER DEFAULT 0
)
""")
conn.commit()

# Bot setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Sync slash commands
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

# /add command
@bot.tree.command(name="add", description="Add points to a user")
@app_commands.describe(user="User to add points to", amount="Number of points")
async def add(interaction: discord.Interaction, user: discord.User, amount: int):
    c.execute("INSERT INTO points (user_id, points) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET points = points + ?",
              (str(user.id), amount, amount))
    conn.commit()
    await interaction.response.send_message(f"Added {amount} points to {user.mention}")

# /sub command
@bot.tree.command(name="sub", description="Subtract points from a user")
@app_commands.describe(user="User to subtract points from", amount="Number of points")
async def sub(interaction: discord.Interaction, user: discord.User, amount: int):
    c.execute("INSERT INTO points (user_id, points) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET points = points - ?",
              (str(user.id), -amount, -amount))  # Use negative to subtract
    conn.commit()
    await interaction.response.send_message(f"Subtracted {amount} points from {user.mention}")

# /points command
@bot.tree.command(name="points", description="Check your points")
@app_commands.describe(user="User to check points for (optional)")
async def points(interaction: discord.Interaction, user: discord.User = None):
    target = user or interaction.user
    c.execute("SELECT points FROM points WHERE user_id = ?", (str(target.id),))
    result = c.fetchone()
    await interaction.response.send_message(f"{target.mention} has {result[0] if result else 0} points")

bot.run(TOKEN)
