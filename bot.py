import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import requests
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

# =====================================================================
# LLEVANTAR UN SERVIDOR WEB FALSO PARA RENDER (Evita que el bot se apague)
# =====================================================================
def run_dummy_server():
    class DummyHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Bot activo y funcionando correctamente.")

    # Render asigna automáticamente un puerto en la variable de entorno PORT (suele ser 10000)
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    print(f" Servidor web falso escuchando en el puerto {port}")
    server.serve_forever()

# Iniciamos el servidor en un hilo secundario para que no bloquee al bot
threading.Thread(target=run_dummy_server, daemon=True).start()
# =====================================================================

# 1. Carga las variables de entorno
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
FOOTBALL_API_KEY = os.getenv('FOOTBALL_API_KEY')

# 2. Configuración de Intents y Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 3. Configuración de API-Football
URL_STANDINGS = "https://api-sports.io"
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
    # ID de LA LIGA = 140 | Temporada 2026
    params = {"league": "140", "season": "2026"}
    
    response = requests.get(URL_STANDINGS, headers=HEADERS, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        try:
            # Navegamos en el JSON para obtener la lista de posiciones
            # Nota: Aseguramos la estructura habitual de API-Football
            league_data = data["response"][0]["league"]
            standings = league_data["standings"][0] # Suele venir como una lista dentro de lista
            
            # Crear un mensaje incrustado (Embed) para que se vea ordenada en Discord
            embed = discord.Embed(
                title=f"Clasificación de {league_data['name']} (Temporada 2026)",
                color=discord.Color.blue()
            )
            
            if league_data.get('logo'):
                embed.set_thumbnail(url=league_data['logo'])
                
            tabla_texto = "Pos. | Equipo               | Pts | PJ\n"
            tabla_texto += "---------------------------------------\n"
            
            for team in standings:
                rank = str(team['rank']).rjust(4)
                name = team['team']['name'][:20].ljust(20)
                points = str(team['points']).ljust(3)
                played = str(team['all']['played'])
                
                tabla_texto += f"{rank} | {name} | {points} | {played}\n"
                
            embed.description = f"```\n{tabla_texto}\n```"
            await ctx.send(embed=embed)
            
        except (IndexError, KeyError) as e:
            print(f"Error de estructura JSON: {e}")
            await ctx.send("No se encontraron datos de la tabla clasificatoria en este momento. ⚽")
    else:
        await ctx.send("Error al conectar con la API de fútbol. Inténtalo más tarde. ❌")

# 6. Único punto de ejecución
bot.run(TOKEN)
