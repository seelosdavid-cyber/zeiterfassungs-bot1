import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

import discord
from discord.ext import commands, tasks
import requests

# 1️⃣ Mini-Webserver für Render (statt Flask)
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot ist online!")
        return

def keep_alive():
    def run():
        port = int(os.environ.get("PORT", 8080))
        server = HTTPServer(('', port), handler)
        print(f"🟢 Keep-alive Server läuft auf Port {port}")
        server.serve_forever()

    t = Thread(target=run)
    t.start()


# 2️⃣ Discord-Bot Setup
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzxvGrY5aGScZXJ0aPowe7FLTTAA_FiSxMNd5gnqASZgyIDyd8WYbQ7WmZjufwMDUY9NA/exec"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


def send_to_sheet(user, typ):
    data = {"user": user, "type": typ}
    try:
        res = requests.post(WEBHOOK_URL, json=data)
        print(f"📤 An Google Sheet gesendet: {res.text}")
    except Exception as e:
        print("❌ Fehler beim Senden an Google Sheet:", e)


@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} ist online")
    reminder.start()


@bot.command()
async def start(ctx):
    send_to_sheet(ctx.author.name, "Start")
    await ctx.send(f"⏱️ Startzeit für {ctx.author.name} gespeichert.")


@bot.command()
async def stop(ctx):
    send_to_sheet(ctx.author.name, "Stop")
    await ctx.send(f"🛑 Endzeit für {ctx.author.name} gespeichert.")


# 3️⃣ Täglicher Reminder um 10:00 Uhr
@tasks.loop(minutes=1)
async def reminder():
    now = datetime.now()
    if now.hour == 10 and now.minute == 0:
        for guild in bot.guilds:
            for channel in guild.text_channels:
                if "zeiterfassung" in channel.name:
                    await channel.send("⏰ Guten Morgen! Vergiss nicht `!start` einzugeben 😄")



# 4️⃣ Start
keep_alive()
bot.run(DISCORD_TOKEN)
