import discord
from discord.ext import commands
import json
import os

bot.run(os.getenv("DISCORD_TOKEN"))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "points.json"

# Load or create data file
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def add(ctx, member: discord.Member, amount: int):
    data = load_data()
    user_id = str(member.id)

    data[user_id] = data.get(user_id, 0) + amount
    save_data(data)

    await ctx.send(f"{member.mention} now has {data[user_id]} points.")

@bot.command()
async def sub(ctx, member: discord.Member, amount: int):
    data = load_data()
    user_id = str(member.id)

    data[user_id] = data.get(user_id, 0) - amount
    save_data(data)

    await ctx.send(f"{member.mention} now has {data[user_id]} points.")

@bot.command()
async def points(ctx, member: discord.Member = None):
    member = member or ctx.author
    data = load_data()
    user_id = str(member.id)

    points = data.get(user_id, 0)
    await ctx.send(f"{member.mention} has {points} points.")

bot.run("YOUR_BOT_TOKEN")
