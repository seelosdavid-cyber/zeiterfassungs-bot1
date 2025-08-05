from flask import Flask
from threading import Thread
from datetime import datetime
import os
import discord
from discord.ext import commands, tasks
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from dotenv import load_dotenv

# Mini-Webserver zum "am Leben halten"
app = Flask('')

@app.route('/')
def home():
    return "Bot ist online!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Webserver starten
keep_alive()

# KEIN load_dotenv() auf Render nötig
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Deine Google Webhook-URL
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzxvGrY5aGScZXJ0aPowe7FLTTAA_FiSxMNd5gnqASZgyIDyd8WYbQ7WmZjufwMDUY9NA/exec"

# Bot initialisieren
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def send_to_sheet(user, typ):
    data = {"user": user, "type": typ}
    try:
        res = requests.post(WEBHOOK_URL, json=data)
        print(f"Google Sheet Antwort: {res.text}")
    except Exception as e:
        print("Fehler beim Senden an Google Sheet:", e)

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

# Reminder um 10:00 Uhr
@tasks.loop(minutes=1)
async def reminder():
    now = datetime.now()
    if now.hour == 10 and now.minute == 0:
        for guild in bot.guilds:
            for channel in guild.text_channels:
                if "zeiterfassung" in channel.name:
                    await channel.send(
                        "⏰ Guten Morgen! Vergiss nicht `!start` einzugeben 😄"
                    )

# ✅ Bot starten!
bot.run(DISCORD_TOKEN)
