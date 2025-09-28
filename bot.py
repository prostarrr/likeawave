import discord
from discord import app_commands
from discord.ext import commands  # <-- Import the commands extension
import os

# --- NEW IMPORTS for the Web Service part ---
import asyncio
from fastapi import FastAPI
import uvicorn

# =================================================================================
# --- CONFIGURATION: PASTE YOUR VALUES HERE ---
# =================================================================================

SERVER_ID = 1381485776583528481
ROLE_TO_GIVE_ID = 1421985165453824140
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

# 1. We need to enable the 'message_content' intent to read prefix commands.
intents = discord.Intents.default()
intents.message_content = True  # <-- THIS IS THE CRUCIAL INTENT

# 2. We now use commands.Bot, which handles both prefix and slash commands.
bot = commands.Bot(command_prefix="?", intents=intents)

# The command tree is now accessed via bot.tree
tree = bot.tree

# We use @bot.event instead of @client.event
@bot.event
async def on_ready():
    guild = discord.Object(id=SERVER_ID)
    await tree.sync(guild=guild)
    print(f"Logged in as {bot.user}. Commands synced to server {SERVER_ID}.")
    print("Bot is ready to receive slash and prefix commands.")

# =================================================================================
# --- SLASH COMMAND: /retrieve --- (No changes here)
# =================================================================================
@tree.command(
    name="retrieve",
    description="No need for explanation.",
    guild=discord.Object(id=SERVER_ID)
)
@app_commands.describe(code="You know.")
async def retrieve_command(interaction: discord.Interaction, code: str):
    # This command's logic remains unchanged.
    if code == CORRECT_CODE:
        member = interaction.user
        guild = interaction.guild
        role_to_give = guild.get_role(ROLE_TO_GIVE_ID)
        if role_to_give is None:
            await interaction.response.send_message("??", ephemeral=True)
            return
        if role_to_give in member.roles:
            await interaction.response.send_message("No point.", ephemeral=True)
            return
        try:
            await member.add_roles(role_to_give)
            await interaction.response.send_message(f"Continue. Or dont.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("??", ephemeral=True)
        except Exception:
            await interaction.response.send_message("??", ephemeral=True)
    else:
        await interaction.response.send_message("Wrong.", ephemeral=True)

# =================================================================================
# --- NEW PREFIX COMMAND: ?say ---
# =================================================================================
@bot.command(name="say")
@commands.has_permissions(manage_messages=True) # Restricts to users with "Manage Messages" permission
async def say_prefix_command(ctx: commands.Context, channel: discord.TextChannel, *, message: str):
    """
    Sends a message to a specific channel. Usage: ?say #channel Your message here.
    This command is hidden from the slash command list.
    """
    try:
        await channel.send(message)
        # Add a checkmark reaction to the user's command message to confirm it was sent
        await ctx.message.add_reaction("✅")
    except discord.Forbidden:
        await ctx.reply(f"❌ Error: I don't have permission to send messages in {channel.mention}.")
    except Exception as e:
        await ctx.reply(f"An unexpected error occurred: {e}")

# Error handler for the ?say prefix command
@say_prefix_command.error
async def on_say_prefix_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("No")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(f"?")
    elif isinstance(error, commands.ChannelNotFound):
        await ctx.reply(f"?")

# =================================================================================
# --- WEB SERVER SETUP (to satisfy Render) --- (No changes here)
# =================================================================================

app = FastAPI()
@app.get("/")
async def health_check():
    return {"status": "OK", "bot_status": "Running" if bot.is_ready() else "Starting"}

async def run_bot_and_server():
    # We now use bot.start() instead of client.start()
    bot_task = asyncio.create_task(bot.start(BOT_TOKEN))
    port = int(os.environ.get("PORT", 8080))
    config = uvicorn.Config(app, host="0.0.0.0", port=port)
    server = uvicorn.Server(config)
    await asyncio.gather(bot_task, server.serve())

if __name__ == "__main__":
    asyncio.run(run_bot_and_server())