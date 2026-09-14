import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import requests

# 1. Carga las variables de entorno
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
FOOTBALL_API_KEY = os.getenv('FOOTBALL_API_KEY')

# 2. Configuración de Intents y Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 3. Configuración de API-Football
URL_STANDINGS = "https://hosted.com" # Asegúrate de que esta URL sea la correcta de tu proveedor
HEADERS = {
    'x-rapidapi-host': 'v3.football.api-sports.io',
    'x-rapidapi-key': FOOTBALL_API_KEY
}

# 4. Eventos del Bot
@bot.event
async def on_ready():
    print(f'{bot.user} online y listo para el chiringuito!')

# 5. Comandos del Bot
@bot.command(name="clasificacion")
async def clasificacion(ctx):
    # ID de LA LIGA = 140 | Temporada 2026/2027
    params = {"league": "140", "season": "2026"}
    
    response = requests.get(URL_STANDINGS, headers=HEADERS, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        try:
            # Navegamos en el JSON para obtener la lista de posiciones
            league_data = data["response"][0]["league"]
            standings = league_data["standings"][0]
            
            # Crear un mensaje incrustado (Embed) para que se vea ordenada en Discord
            embed = discord.Embed(
                title=f"Clasificación de {league_data['name']} (Temporada 2026/27)",
                color=discord.Color.blue()
            )
            
            if league_data.get('logo'):
                embed.set_thumbnail(url=league_data['logo'])
                
            tabla_texto = "Pos. | Equipo               | Pts | PJ\n"
            tabla_texto += "---------------------------------------\n"
            
            for team in standings:
                rank = str(team['rank']).rjust(4)
                # Cortamos nombres largos a 20 caracteres para que encaje visualmente
                name = team['team']['name'][:20].ljust(20)
                points = str(team['points']).ljust(3)
                played = str(team['all']['played'])
                
                tabla_texto += f"{rank} | {name} | {points} | {played}\n"
                
            embed.description = f"```\n{tabla_texto}\n```"
            await ctx.send(embed=embed)
            
        except (IndexError, KeyError):
            await ctx.send("No se encontraron datos de la tabla clasificatoria en este momento. ⚽")
    else:
        await ctx.send("Error al conectar con la API de fútbol. Inténtalo más tarde. ❌")

# 6. Único punto de ejecución (Siempre al final del archivo)
bot.run(TOKEN)
