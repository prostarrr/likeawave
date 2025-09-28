import discord
from discord import app_commands

# =================================================================================
# --- CONFIGURATION: PASTE YOUR VALUES HERE ---
#
# This is the simplified setup. Fill in these four variables directly.
# =================================================================================

# 1. Get your Bot Token from the "Bot" page on the Discord Developer Portal.
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# 2. Get your Server ID by right-clicking your server icon and selecting "Copy Server ID".
#    (You must have Developer Mode enabled in Discord Settings > Advanced)
SERVER_ID = 123456789012345678

# 3. Get the Role ID from Server Settings > Roles, right-click the role, and "Copy Role ID".
ROLE_TO_GIVE_ID = 987654321098765432

# 4. Choose the secret code users will have to type to get the role.
CORRECT_CODE = "SECRET-CODE-123"

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
    # This syncs the slash command to your specific server.
    await tree.sync(guild=discord.Object(id=SERVER_ID))
    

# This defines the /retrieve slash command.
@tree.command(
    name="retrieve",
    description="What?",
    guild=discord.Object(id=SERVER_ID) # This makes the command available only in your server
)
@app_commands.describe(code="Somethings can't be answered.")
async def retrieve_command(interaction: discord.Interaction, code: str):
    # This makes the bot's reply visible only to the person who used the command.
    await interaction.response.defer(ephemeral=True)

    # Check if the provided code matches the correct one.
    if code == CORRECT_CODE:
        member = interaction.user
        guild = interaction.guild
        role_to_give = guild.get_role(ROLE_TO_GIVE_ID)

        # Safety check: Does the role actually exist?
        if role_to_give is None:
            await interaction.followup.send("??")
            return

        # Check if the user already has the role to avoid unnecessary actions.
        if role_to_give in member.roles:
            await interaction.followup.send(f"...")
            return

        # Try to add the role to the user.
        try:
            await member.add_roles(role_to_give)
            await interaction.followup.send(f"Moving on.")
        except discord.Forbidden:
            # This error occurs if the bot's role is not high enough in the role hierarchy.
            await interaction.followup.send("??")
        except Exception as e:
            # Catch any other unexpected problems.
            await interaction.followup.send("??")

    else:
        # This message is sent if the code is wrong.
        await interaction.followup.send("No.")


# This line starts the bot.
client.run(BOT_TOKEN)