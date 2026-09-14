import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import requests
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

# =====================================================================
# SERVIDOR WEB FALSO PARA RENDER
# =====================================================================
def run_dummy_server():
    class DummyHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Bot activo y funcionando correctamente.")

    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    print(f" Servidor web falso escuchando en el puerto {port}")
    server.serve_forever()

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

# 3. Configuración de API-Football (URL correcta oficial)
URL_STANDINGS = "https://api-sports.io"
HEADERS = {
    'x-apisports-key': FOOTBALL_API_KEY
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
    
    # Avisamos al chat de que estamos buscando para evitar impaciencias
    await ctx.send("📊 Buscando la clasificación de LaLiga... Por favor, espera.")
    
    try:
        response = requests.get(URL_STANDINGS, headers=HEADERS, params=params)
        print(f"API Status Code: {response.status_code}") # Log en Render
        
        if response.status_code == 200:
            data = response.json()
            
            # Si la API responde pero el token está mal o no hay datos, viene en la sección 'errors'
            if data.get("errors"):
                print(f"Errores devueltos por la API: {data['errors']}")
                await ctx.send(f"❌ Error de la API de fútbol: {data['errors']}")
                return

            # Verificamos si hay respuesta válida
            if not data.get("response"):
                await ctx.send("❌ No se encontraron datos para LaLiga en la temporada especificada.")
                return

            # Extracción correcta del formato de API-Football
            # Estructura real: data["response"][0]["league"]["standings"][0] -> Lista de equipos
            league_info = data["response"][0]["league"]
            standings = league_info["standings"][0] # La API mete la lista dentro de otra lista
            
            # Crear el mensaje incrustado (Embed)
            embed = discord.Embed(
                title=f"🏆 Clasificación de {league_info['name']} (Temporada 2026/27)",
                color=discord.Color.blue()
            )
            
            if league_info.get('logo'):
                embed.set_thumbnail(url=league_info['logo'])
                
            tabla_texto = "Pos. | Equipo               | Pts | PJ\n"
            tabla_texto += "---------------------------------------\n"
            
            # Construimos la tabla línea por línea (Máximo 20 equipos)
            for team in standings[:20]:
                rank = str(team['rank']).rjust(4)
                name = team['team']['name'][:20].ljust(20)
                points = str(team['points']).ljust(3)
                played = str(team['all']['played'])
                
                tabla_texto += f"{rank} | {name} | {points} | {played}\n"
                
            embed.description = f"```\n{tabla_texto}\n```"
            await ctx.send(embed=embed)
            
        else:
            await ctx.send(f"❌ Error al conectar con la API de fútbol (Código HTTP: {response.status_code}).")
            
    except Exception as e:
        print(f"Error crítico en el comando: {e}")
        await ctx.send("❌ Ocurrió un error inesperado al procesar la clasificación.")

# 6. Único punto de ejecución
bot.run(TOKEN)
