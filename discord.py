import os
import discord
from discord.ext import commands
from dotenv import load_data  # Si usas python-dotenv usa: load_dotenv()

# Carga las variables del archivo .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# ... Aquí va el resto de tus comandos de fútbol ...

bot.run(TOKEN)

