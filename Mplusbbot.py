import discord
from discord.ext import commands
from discord.ui import Button, View

# Bot-Setup mit notwendigen Rechten (Intents)
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

class MPlusGroup:
    """Hält den Zustand einer einzelnen M+ Gruppe fest."""
    def __init__(self, dungeon, key_level, date_time, creator):
        self.dungeon = dungeon
        self.key_level = key_level
        self.date_time = date_time
        self.creator = creator
        
        # Plätze für die Rollen
        self.tank = None
        self.healer = None
        self.dps = []  # Maximal 3

    def to_embed(self):
        """Erstellt ein schickes Discord Embed für die Anzeige."""
        embed = discord.Embed(
            title=f"⚔️ Mythic+ Gruppe: {self.dungeon} +{self.key_level}",
            description= f"**Termin:** {self.date_time}\n**Erstellt von:** {self.creator.mention}",
            color=discord.Color.blue()
        )
        
        # Rollen-Status anzeigen
        tank_status = self.tank.mention if self.tank else "*Gesucht*"
        healer_status = self.healer.mention if self.healer else "*Gesucht*"
        
        # DPS Liste formatieren (immer 3 Zeilen anzeigen)
        dps_slots = []
        for i in range(3):
            if i < len(self.dps):
                dps_slots.append(self.dps[i].mention)
            else:
                dps_slots.append("*Gesucht*")
        
        embed.add_field(name="🛡️ Tank (0/1)", value=tank_status, inline=False) if not self.tank else embed.add_field(name="🛡️ Tank (1/1)", value=tank_status, inline=False)
        embed.add_field(name="🌿 Heiler (0/1)", value=healer_status, inline=False) if not self.healer else embed.add_field(name="🌿 Heiler (1/1)", value=healer_status, inline=False)
        embed.add_field(name=f"⚔️ DPS ({len(self.dps)}/3)", value="\n".join(dps_slots), inline=False)
        
        return embed

class GroupView(View):
    """Die interaktiven Buttons unter dem Embed."""
    def __init__(self, group_data):
        super().__init__(timeout=None) # Kein Timeout, Button bleibt aktiv
        self.group = group_data

    # Hilfsfunktion, um User aus anderen Rollen zu entfernen, wenn sie wechseln
    def _remove_user_from_all(self, user):
        if self.group.tank == user: self.group.tank = None
        if self.group.healer == user: self.group.healer = None
        if user in self.group.dps: self.group.dps.remove(user)

    @discord.ui.button(label="Tank", style=discord.ButtonStyle.grey, emoji="🛡️")
    async def tank_button(self, interaction: discord.Interaction, button: Button):
        self._remove_user_from_all(interaction.user)
        if not self.group.tank:
            self.group.tank = interaction.user
            await interaction.response.edit_message(embed=self.group.to_embed(), view=self)
        else:
            await interaction.response.send_message("Der Tank-Slot ist schon voll!", ephemeral=True)

    @discord.ui.button(label="Heiler", style=discord.ButtonStyle.grey, emoji="🌿")
    async def healer_button(self, interaction: discord.Interaction, button: Button):
        self._remove_user_from_all(interaction.user)
        if not self.group.healer:
            self.group.healer = interaction.user
            await interaction.response.edit_message(embed=self.group.to_embed(), view=self)
        else:
            await interaction.response.send_message("Der Heiler-Slot ist schon voll!", ephemeral=True)

    @discord.ui.button(label="DPS", style=discord.ButtonStyle.grey, emoji="⚔️")
    async def dps_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user in self.group.dps:
            # Wenn man nochmal klickt, meldet man sich ab
            self.group.dps.remove(interaction.user)
            await interaction.response.edit_message(embed=self.group.to_embed(), view=self)
            return

        self._remove_user_from_all(interaction.user)
        if len(self.group.dps) < 3:
            self.group.dps.append(interaction.user)
            await interaction.response.edit_message(embed=self.group.to_embed(), view=self)
        else:
            await interaction.response.send_message("Die DPS-Slots sind schon voll!", ephemeral=True)

    @discord.ui.button(label="Abmelden", style=discord.ButtonStyle.red)
    async def leave_button(self, interaction: discord.Interaction, button: Button):
        self._remove_user_from_all(interaction.user)
        await interaction.response.edit_message(embed=self.group.to_embed(), view=self)


@bot.event
async def on_ready():
    print(f'Bot ist online als {bot.user}')
    try:
        # Synchronisiert die Slash-Commands mit Discord
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

# Der Slash-Command zum Erstellen einer Gruppe
@bot.tree.command(name="mplus", description="Erstelle eine neue Mythic+ Gruppensuche")
async def mplus(interaction: discord.Interaction, dungeon: str, key_level: int, date_time: str):
    # Erstelle das Daten-Objekt für die Gruppe
    new_group = MPlusGroup(dungeon, key_level, date_time, interaction.user)
    
    # Erstelle die View mit den Buttons
    view = GroupView(new_group)
    
    # Sende das Embed mit den Buttons in den Kanal
    await interaction.response.send_message(embed=new_group.to_embed(), view=view)

# ERSETZEDEIN_BO DIESEN TOKEN MIT DEINEM EIGENEN AUS DEM DEVELOPER PORTAL
bot.run('')