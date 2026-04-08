import os
import sqlite3
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import requests

load_dotenv()

# Discord Bot Configuration
TOKEN = os.getenv("DISCORD_TOKEN")
DB_PATH = os.getenv("DB_PATH", "points.sqlite")

# LM Studio Configuration
LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1/chat/completions")
LM_MODEL = os.getenv("LM_MODEL", "lmstudio-community/llama-3.2-3b-instruct-gguf")

# Conversation memory: {user_id: [{"role": str, "content": str}, ...]}
conversation_history = {}

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


def get_conversation_context(user_id: str, max_messages: int = 10):
    """Get recent conversation history for a user."""
    if user_id not in conversation_history:
        return []
    
    # Return last N messages
    return conversation_history[user_id][-max_messages:]


def add_to_conversation(user_id: str, role: str, content: str):
    """Add a message to the conversation history."""
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    
    conversation_history[user_id].append({"role": role, "content": content})
    
    # Keep only last 20 messages to prevent memory issues
    if len(conversation_history[user_id]) > 20:
        conversation_history[user_id] = conversation_history[user_id][-20:]


def get_system_prompt():
    """Get the system prompt for the AI assistant."""
    return """You are a helpful Discord bot assistant that can also help with point tracking. 
You're friendly and conversational, but concise in your responses (suitable for Discord).
If someone asks about points, you can explain how to use /add, /sub, and /points commands.
Keep responses under 200 words when possible."""


async def call_lm_api(user_id: str, user_message: str) -> tuple[str, bool]:
    """Call LM Studio API and return the response text and success status."""
    
    # Get conversation context
    messages = get_conversation_context(user_id)
    
    # Add system prompt if this is a new conversation or first message
    if not messages:
        messages.insert(0, {"role": "system", "content": get_system_prompt()})
    
    # Add user's message to history
    messages.append({"role": "user", "content": user_message})
    
    try:
        response = requests.post(
            LM_STUDIO_URL,
            json={
                "model": LM_MODEL,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 500,
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
            
            # Add AI response to conversation history
            messages.append({"role": "assistant", "content": ai_response})
            
            return ai_response, True
        else:
            error_msg = f"LM Studio returned status {response.status_code}: {response.text}"
            add_to_conversation(user_id, "system", f"[Error: {error_msg}]")
            return f"Sorry, I couldn't connect to the AI. Please make sure LM Studio is running and accessible at {LM_STUDIO_URL}", False
            
    except requests.exceptions.ConnectionError:
        error_msg = "Could not connect to LM Studio. Make sure it's running with the server enabled."
        add_to_conversation(user_id, "system", f"[Error: {error_msg}]")
        return f"Sorry, I couldn't connect to LM Studio. Please ensure:\n1. LM Studio is running\n2. The local server is enabled in LM Studio settings\n3. The model is loaded", False
        
    except requests.exceptions.Timeout:
        error_msg = "Request timed out"
        add_to_conversation(user_id, "system", f"[Error: {error_msg}]")
        return "Sorry, the request took too long. Please try again.", False
        
    except Exception as e:
        error_msg = str(e)
        add_to_conversation(user_id, "system", f"[Error: {error_msg}]")
        return f"An error occurred: {e}", False


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
    await interaction.response.send_message(f"Added {amount} shrimp scampi points to {user.mention}")


# /sub command
@bot.tree.command(name="sub", description="Subtract points from a user")
@app_commands.describe(user="User to subtract points from", amount="Number of points")
async def sub(interaction: discord.Interaction, user: discord.User, amount: int):
    c.execute("INSERT INTO points (user_id, points) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET points = points - ?",
              (str(user.id), -amount, -amount))  # Use negative to subtract
    conn.commit()
    await interaction.response.send_message(f"Subtracted {amount} shrimp scampi points from {user.mention}")


# /points command
@bot.tree.command(name="points", description="Check your points")
@app_commands.describe(user="User to check points for (optional)")
async def points(interaction: discord.Interaction, user: discord.User = None):
    target = user or interaction.user
    c.execute("SELECT points FROM points WHERE user_id = ?", (str(target.id),))
    result = c.fetchone()
    await interaction.response.send_message(f"{target.mention} has {result[0] if result else 0} shrimp scampi points")


# /chat command - AI Chat with local LLM
@bot.tree.command(name="chat", description="Chat with the AI assistant powered by your local LM Studio")
@app_commands.describe(message="Your message to the AI")
async def chat(interaction: discord.Interaction, message: str = None):
    """Handle AI chat requests."""
    
    # If no message provided, show usage help
    if not message:
        embed = discord.Embed(
            title="💬 AI Chat Assistant",
            description="Chat with the AI powered by your local LM Studio model.",
            color=discord.Color.blue()
        )
        embed.add_field(name="Usage", value="/chat [your message here]")
        embed.add_field(name="Example", value="/chat What can you help me with?")
        embed.set_footer(text=f"Connected to: {LM_MODEL}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Show typing indicator while processing
    await interaction.response.send_message("Thinking...", ephemeral=True)
    
    try:
        # Call the LM Studio API
        response_text, success = await call_lm_api(str(interaction.user.id), message)
        
        # Truncate response if too long for Discord (max 2000 chars)
        if len(response_text) > 1800:
            response_text = response_text[:1797] + "..."
        
        await interaction.followup.send(response_text, ephemeral=True)
        
    except Exception as e:
        await interaction.followup.send(f"An error occurred while processing your request: {e}", ephemeral=True)


# /clearchat command - Clear conversation history
@bot.tree.command(name="clearchat", description="Clear your AI chat conversation history")
async def clear_chat(interaction: discord.Interaction):
    """Clear the user's conversation history."""
    
    if interaction.user.id in conversation_history:
        del conversation_history[interaction.user.id]
        await interaction.response.send_message("Your conversation history has been cleared.", ephemeral=True)
    else:
        await interaction.response.send_message("You don't have any conversation history to clear.", ephemeral=True)


# Graceful shutdown handler
import atexit

@atexit.register
def cleanup():
    """Clean up resources on exit."""
    conn.close()
    print("Database connection closed.")


bot.run(TOKEN)