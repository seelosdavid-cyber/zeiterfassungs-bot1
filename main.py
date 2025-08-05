from flask import Flask
from threading import Thread
from datetime import datetime
import discord
from discord.ext import commands, tasks
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import os
from dotenv import load_dotenv

# KEIN load_dotenv() auf Replit nötig

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Deine Google Webhook-URL hier einfügen:
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
                        "⏰ Guten Morgen! Vergiss nicht `!start` einzugeben 😄")
app = Flask('')

@app.route('/')
def home():
    return "Bot ist online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
keep_alive()


# ✅ Bot starten!
bot.run(DISCORD_TOKEN)
