# PointBot - Discord Bot with AI Chat

A Discord bot for tracking "shrimp scampi points" with optional AI chat functionality powered by local LLMs via LM Studio.

## Features

- **Point Tracking**: Add, subtract, and view user points using slash commands
- **AI Chat**: Chat with an AI assistant running locally on your machine
- **Conversation Memory**: The bot remembers conversation context for each user

## Installation

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd pointbot
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

5. Edit `.env` and add your Discord bot token:
   ```
   DISCORD_TOKEN=your_bot_token_here
   ```

## LM Studio Setup (for AI Chat)

1. **Install LM Studio**: Download from [https://lmstudio.ai](https://lmstudio.ai)

2. **Download a model**: 
   - Open LM Studio and go to the search tab
   - Search for a model (e.g., "Llama 3", "Mistral")
   - Download a model you like

3. **Enable Local Server**:
   - Go to the server tab (left sidebar, icon looks like a server)
   - Select your downloaded model at the top
   - Click "Start Server"
   - By default, it runs on `http://localhost:1234`

4. **Configure PointBot** (optional):
   
   Edit your `.env` file to customize:
   ```
   # Use defaults if you don't change these:
   LM_STUDIO_URL=http://localhost:1234/v1/chat/completions
   
   # Change model if needed - must match a loaded GGUF model in LM Studio
   LM_MODEL=your-chosen-model-name
   ```

## Usage

### Point Commands (existing)

- `/add @user 5` - Add 5 points to the mentioned user
- `/sub @user 3` - Subtract 3 points from the mentioned user  
- `/points [@user]` - View your or another user's points

### AI Chat Commands (new)

- `/chat [message]` - Chat with the AI assistant
  ```
  /chat What can you help me with?
  ```

- `/clearchat` - Clear your conversation history with the AI

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `DISCORD_TOKEN` | (required) | Your Discord bot token from [Discord Developer Portal](https://discord.com/developers/applications) |
| `DB_PATH` | `points.sqlite` | Path to the SQLite database file |
| `LM_STUDIO_URL` | `http://localhost:1234/v1/chat/completions` | LM Studio API endpoint URL |
| `LM_MODEL` | `lmstudio-community/llama-3.2-3b-instruct-gguf` | Model name to use (must match loaded model in LM Studio) |

## Troubleshooting

### AI Chat not working?

1. **Check LM Studio is running**: Look for the server indicator in LM Studio
2. **Verify the URL**: Ensure `LM_STUDIO_URL` matches your LM Studio endpoint
3. **Model must be loaded**: The model should appear as "loaded" in LM Studio's server tab
4. **Firewall/Antivirus**: May block local connections - try temporarily disabling

### Bot not responding to commands?

1. **Check token**: Ensure `DISCORD_TOKEN` is correct and hasn't expired
2. **Re-register commands**: Delete the bot from your server and re-invite it
3. **Permissions**: Ensure bot has "Send Messages" and "Use Slash Commands" permissions

## Architecture

```
┌─────────────────┐
│   Discord API   │
└────────┬────────┘
         │
         ▼
┌──────────────────────┐
│     bot.py           │
│  - Point commands    │
│  - AI chat command   │
│  - Conversation mgmt │
└────────┬─────────────┘
         │
         ├──────────────┐
         ▼              ▼
┌─────────────────┐ ┌──────────────────────┐
│  SQLite DB      │ │ LM Studio (Local)    │
│  points.sqlite  │ │ port: 1234           │
└─────────────────┘ └──────────────────────┘
```

## License

MIT License - Feel free to use and modify as needed!