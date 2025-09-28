import discord
from discord import app_commands
import os

# =================================================================================
# --- CONFIGURATION: PASTE YOUR VALUES HERE ---
#
# This is the simplified setup. Fill in these three variables directly.
# The Bot Token will be set as an environment variable on your hosting platform (Render).
# =================================================================================

# 1. Get your Server ID by right-clicking your server icon and selecting "Copy Server ID".
#    (You must have Developer Mode enabled in Discord Settings > Advanced)
SERVER_ID = 755559107964043364

# 2. Get the Role ID from Server Settings > Roles, right-click the role, and "Copy Role ID".
ROLE_TO_GIVE_ID = 1421736616896237588

# 3. Choose the secret code users will have to type to get the role.
CORRECT_CODE = "teslasintherain"

# =================================================================================
# --- ENVIRONMENT VARIABLE ---
# (This is the only value you'll set on Render)
# =================================================================================

BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
if not BOT_TOKEN:
    print("FATAL_ERROR: DISCORD_BOT_TOKEN environment variable is not set.")
    exit()

# =================================================================================
# --- END OF CONFIGURATION ---
# (You shouldn't need to change anything below this line)
# =================================================================================

# This sets up the bot's connection to Discord
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# This event runs once the bot is online and ready.
@client.event
async def on_ready():
    # This syncs the slash command specifically to your server.
    # It's faster and more reliable for a single-server bot.
    guild = discord.Object(id=SERVER_ID)
    await tree.sync(guild=guild)
    print(f"Logged in as {client.user}. Commands synced to server {SERVER_ID}.")
    

# This defines the /retrieve slash command.
@tree.command(
    name="retrieve",
    description="Nothing important.",
    guild=discord.Object(id=SERVER_ID) # This makes the command available only in your server
)
@app_commands.describe(code="The secret code you were given.")
async def retrieve_command(interaction: discord.Interaction, code: str):
    # Check if the provided code matches the correct one.
    if code == CORRECT_CODE:
        member = interaction.user # The user who ran the command
        guild = interaction.guild
        role_to_give = guild.get_role(ROLE_TO_GIVE_ID)

        # Safety check: Does the role actually exist on the server?
        if role_to_give is None:
            await interaction.response.send_message(
                "??",
                ephemeral=True # Visible only to the user
            )
            return

        # Check if the user already has the role.
        if role_to_give in member.roles:
            await interaction.response.send_message(
                "What?",
                ephemeral=True
            )
            return

        # Try to add the role to the user.
        try:
            await member.add_roles(role_to_give)
            await interaction.response.send_message(
                f"Continue.",
                ephemeral=True
            )
        except discord.Forbidden:
            # This error means the bot's role is not high enough in the hierarchy.
            await interaction.response.send_message(
                "???",
                ephemeral=True
            )
        except Exception:
            await interaction.response.send_message(
                "???",
                ephemeral=True
            )
    else:
        # This message is sent if the code is wrong.
        await interaction.response.send_message(
            "Wrong.",
            ephemeral=True
        )

# This line starts the bot using the token from the environment variable.
client.run(BOT_TOKEN)