import discord
from discord import app_commands
import os

# --- NEW IMPORTS for the Web Service part ---
import asyncio
from fastapi import FastAPI
import uvicorn

# =================================================================================
# --- CONFIGURATION: PASTE YOUR VALUES HERE ---
#
# This is the simplified setup. Fill in these three variables directly.
# The Bot Token will be set as an environment variable on your hosting platform (Render).
# =================================================================================

SERVER_ID = 755559107964043364
ROLE_TO_GIVE_ID = 1421736616896237588
CORRECT_CODE = "teslasintherain"

# =================================================================================
# --- ENVIRONMENT VARIABLE ---
# =================================================================================

BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
if not BOT_TOKEN:
    print("FATAL_ERROR: DISCORD_BOT_TOKEN environment variable is not set.")
    exit()

# =================================================================================
# --- DISCORD BOT SETUP ---
# =================================================================================

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    guild = discord.Object(id=SERVER_ID)
    await tree.sync(guild=guild)
    print(f"Logged in as {client.user}. Commands synced to server {SERVER_ID}.")

@tree.command(
    name="retrieve",
    description="Enter the secret code to receive your role.",
    guild=discord.Object(id=SERVER_ID)
)
@app_commands.describe(code="The secret code you were given.")
async def retrieve_command(interaction: discord.Interaction, code: str):
    if code == CORRECT_CODE:
        member = interaction.user
        guild = interaction.guild
        role_to_give = guild.get_role(ROLE_TO_GIVE_ID)

        if role_to_give is None:
            await interaction.response.send_message(
                "Error: The target role could not be found. Please contact an administrator.",
                ephemeral=True
            )
            return

        if role_to_give in member.roles:
            await interaction.response.send_message("You already have this role.", ephemeral=True)
            return

        try:
            await member.add_roles(role_to_give)
            await interaction.response.send_message(
                f"Success! You have been given the '{role_to_give.name}' role.",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "Error: I do not have permission to give out this role. My role must be higher than the one I'm granting.",
                ephemeral=True
            )
        except Exception:
            await interaction.response.send_message(
                "An unexpected error occurred. Please try again later.",
                ephemeral=True
            )
    else:
        await interaction.response.send_message("The code you entered is incorrect.", ephemeral=True)

# =================================================================================
# --- WEB SERVER SETUP (to satisfy Render) ---
# =================================================================================

# Create a FastAPI app instance
app = FastAPI()

# This is the health check endpoint that Render will call
@app.get("/")
async def health_check():
    return {"status": "OK", "bot_status": "Running" if client.is_ready() else "Starting"}

# This function will run both the bot and the web server together
async def run_bot_and_server():
    # Start the Discord bot in the background
    # We use client.start() instead of client.run() because start() is non-blocking
    bot_task = asyncio.create_task(client.start(BOT_TOKEN))

    # Configure and start the Uvicorn web server
    # Render provides the PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    config = uvicorn.Config(app, host="0.0.0.0", port=port)
    server = uvicorn.Server(config)
    
    # Run the web server and the bot task concurrently
    await asyncio.gather(bot_task, server.serve())

# This is the entry point for the script
if __name__ == "__main__":
    asyncio.run(run_bot_and_server())