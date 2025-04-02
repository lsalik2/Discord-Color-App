import os
import discord
from discord import app_commands
from dotenv import load_dotenv

# --------------------- Section: Shared Helper Function ---------------------
def build_ansi_response(message: str, format_value: int, text_color_value: int, background_color_value: int, mobile_friendly: bool = False) -> str:
    """
    Build the ANSI formatted response.
    If mobile_friendly is True, only the raw ANSI code block is returned.
    Otherwise, a preview and a raw block for copy-pasting are provided.
    """
    ansi_code = f"\u001b[{format_value};{text_color_value};{background_color_value}m"
    reset_code = "\u001b[0m"
    if mobile_friendly:
        return f"```ansi\n{ansi_code}{message}{reset_code}\n```"
    else:
        return (
            "Here's your colorized message:\n"
            f"```ansi\n{ansi_code}{message}{reset_code}\n```\n"
            "Raw text for copy-pasting:\n"
            "\`\`\`ansi\n"
            f"{ansi_code}{message}{reset_code}\n"
            "\`\`\`"
        )

# --------------------- Section: Options Choices ---------------------
FORMAT_OPTIONS = [
    app_commands.Choice(name="Normal", value=0),
    app_commands.Choice(name="Bold", value=1),
    app_commands.Choice(name="Underline", value=4)
]

BACKGROUND_COLORS = [
    app_commands.Choice(name="Dark Blue", value=40),
    app_commands.Choice(name="Dark Grey", value=42),
    app_commands.Choice(name="Grey", value=43),
    app_commands.Choice(name="Indigo", value=45),
    app_commands.Choice(name="Light Grey", value=44),
    app_commands.Choice(name="Orange", value=41),
    app_commands.Choice(name="Silver", value=46),
    app_commands.Choice(name="White", value=47)
]

TEXT_COLORS = [
    app_commands.Choice(name="Blue", value=34),
    app_commands.Choice(name="Cyan", value=36),
    app_commands.Choice(name="Green", value=32),
    app_commands.Choice(name="Grey", value=30),
    app_commands.Choice(name="Pink", value=35),
    app_commands.Choice(name="Red", value=31),
    app_commands.Choice(name="White", value=37),
    app_commands.Choice(name="Yellow", value=33)
]

FORMAT_UI_OPTIONS = [
    discord.SelectOption(label="Normal", value="0", description="No special formatting"),
    discord.SelectOption(label="Bold", value="1", description="Bold text"),
    discord.SelectOption(label="Underline", value="4", description="Underlined text")
]

BACKGROUND_UI_OPTIONS = [
    discord.SelectOption(label="Dark Blue", value="40"),
    discord.SelectOption(label="Dark Grey", value="42"),
    discord.SelectOption(label="Grey", value="43"),
    discord.SelectOption(label="Indigo", value="45"),
    discord.SelectOption(label="Light Grey", value="44"),
    discord.SelectOption(label="Orange", value="41"),
    discord.SelectOption(label="Silver", value="46"),
    discord.SelectOption(label="White", value="47")
]

TEXT_UI_OPTIONS = [
    discord.SelectOption(label="Blue", value="34"),
    discord.SelectOption(label="Cyan", value="36"),
    discord.SelectOption(label="Green", value="32"),
    discord.SelectOption(label="Grey", value="30"),
    discord.SelectOption(label="Pink", value="35"),
    discord.SelectOption(label="Red", value="31"),
    discord.SelectOption(label="White", value="37"),
    discord.SelectOption(label="Yellow", value="33")
]

# --------------------- Section: Setup and Intents ---------------------
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# --------------------- Section: Start-up Functions and Debugs ---------------------
@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')
    try:
        print("Syncing commands globally...")
        await tree.sync()
        print("Command sync completed successfully")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    activity = discord.Activity(
        type=discord.ActivityType.listening, 
        name="/chroma"
    )
    await client.change_presence(activity=activity)
    print('Bot is ready!')

# --------------------- Section: /chroma Command ---------------------
@tree.command(name="chroma", description="Create a colorful ANSI code block")
@app_commands.describe(
    message="The message to colorize",
    format="Text formatting",
    background_color="The background color",
    text_color="The color of the text",
    mobile_friendly="Mobile-friendly copy-paste output"
)
@app_commands.choices(
    format=FORMAT_OPTIONS,
    background_color=BACKGROUND_COLORS,
    text_color=TEXT_COLORS,
    mobile_friendly=[app_commands.Choice(name="Yes", value="yes")]
)
async def chroma_command(
    interaction: discord.Interaction, 
    message: str, 
    format: app_commands.Choice[int],
    background_color: app_commands.Choice[int],
    text_color: app_commands.Choice[int],
    mobile_friendly: app_commands.Choice[str] = None
):
    mobile_flag = (mobile_friendly is not None and mobile_friendly.value == "yes")
    response = build_ansi_response(message, format.value, text_color.value, background_color.value, mobile_flag)
    await interaction.response.send_message(response, ephemeral=True)

# --------------------- Section: Context Menu Command ---------------------
@tree.context_menu(name="Colorize Text")
async def colorize_context_menu(
    interaction: discord.Interaction, 
    message: discord.Message
):
    """
    Context menu command that works on messages.
    Right-click on a message -> Apps -> Colorize Text.
    """
    view = SelectionView(message.content if message.content else "Sample text")
    await interaction.response.send_message(
        content="Select below your format, background color, text color (and optionally, a mobile-friendly output), then click **Submit**.",
        view=view,
        ephemeral=True
    )

# --------------------- Section: Custom View with Selects ---------------------
class SelectionView(discord.ui.View):
    """
    A View containing four dropdown selects for Format, Background color,
    Text color, and optional Mobile-friendly output, plus a Submit button.
    """
    def __init__(self, message_text: str):
        super().__init__(timeout=120)
        self.message_text = message_text
        
        # Default values (if user never picks anything)
        self.format_value = 0
        self.background_color_value = 40
        self.text_color_value = 32
        self.mobile_friendly_value = None

        self.add_item(FormatSelect(row=0))
        self.add_item(BackgroundColorSelect(row=1))
        self.add_item(TextColorSelect(row=2))
        self.add_item(MobileFriendlySelect(row=3))
    
    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=4)
    async def submit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        mobile_flag = (self.mobile_friendly_value == "yes")
        response = build_ansi_response(self.message_text, self.format_value, self.text_color_value, self.background_color_value, mobile_flag)
        await interaction.response.defer()
        await interaction.delete_original_response()
        await interaction.followup.send(content=response, ephemeral=True)
        self.stop()

class FormatSelect(discord.ui.Select):
    def __init__(self, row: int = 0):
        super().__init__(
            placeholder="Pick a format...",
            min_values=1,
            max_values=1,
            options=FORMAT_UI_OPTIONS,
            row=row
        )
    
    async def callback(self, interaction: discord.Interaction):
        parent_view = self.view
        if isinstance(parent_view, SelectionView):
            parent_view.format_value = int(self.values[0])
        await interaction.response.defer()

class BackgroundColorSelect(discord.ui.Select):
    def __init__(self, row: int = 1):
        super().__init__(
            placeholder="Pick a background color...",
            min_values=1,
            max_values=1,
            options=BACKGROUND_UI_OPTIONS,
            row=row
        )
    
    async def callback(self, interaction: discord.Interaction):
        parent_view = self.view
        if isinstance(parent_view, SelectionView):
            parent_view.background_color_value = int(self.values[0])
        await interaction.response.defer()

class TextColorSelect(discord.ui.Select):
    def __init__(self, row: int = 2):
        super().__init__(
            placeholder="Pick a text color...",
            min_values=1,
            max_values=1,
            options=TEXT_UI_OPTIONS,
            row=row
        )
    
    async def callback(self, interaction: discord.Interaction):
        parent_view = self.view
        if isinstance(parent_view, SelectionView):
            parent_view.text_color_value = int(self.values[0])
        await interaction.response.defer()

class MobileFriendlySelect(discord.ui.Select):
    def __init__(self, row: int = 3):
        options = [
            discord.SelectOption(label="Yes", value="yes")
        ]
        super().__init__(
            placeholder="Mobile-friendly output? (Optional)",
            min_values=0,
            max_values=1,
            options=options,
            row=row
        )
    
    async def callback(self, interaction: discord.Interaction):
        parent_view = self.view
        if isinstance(parent_view, SelectionView) and self.values:
            parent_view.mobile_friendly_value = self.values[0]
        await interaction.response.defer()

# --------------------- Section: Token Loading ---------------------
def main():
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")
    
    if not token:
        print("Error: DISCORD_TOKEN not found in environment variables")
        return
    
    client.run(token)

if __name__ == "__main__":
    main()