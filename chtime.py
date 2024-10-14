import discord
from discord.ext import commands
import math
import time
import asyncio
import os
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True  # Aktiviert die Nachrichteninhalt-Intents

bossinfo = {
    # meteoric
    "doomclaw": 7,
    "bonehead": 15,
    "redbane": 20,
    "goretusk": 20,
    "coppinger": 20,
    "rockbelly": 15,
    # frozen
    "eye": 30,
    "swampi": 35,
    "woody": 40,
    "chain": 45,
    "grom": 50,
    "pyrus": 60,
    # dragonlord
    "150": 40,
    "155": 50,
    "160": 60,
    "165": 70,
    "170": 80,
    "180": 90,
    # exalted dragonlord
    "onyx": 60,
    "skath": 70,
    "gron": 80,
    "dobby": 90,
    "flappy": 100,
    "phantom": 110,
    "unox": 120,
    "prot": 130
}

bosstimers = {name: 0 for name in bossinfo.keys()}
timerRunning = {name: False for name in bossinfo.keys()}

TOKEN = os.getenv('TOKEN')
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}.')

@bot.event
async def on_command_error(ctx, error):
    await ctx.channel.send('>>> Oh oh! An Error occurred o_o\n Did you maybe forget to enter the boss name?')
    return

@bot.command(name='info')
async def getInfo(ctx):
    message = '>>> **Available commands:**\n'
    message += '```diff\n'
    message += '+ !names              - lists the names of all available bosses\n'
    message += '+ !soon               - lists all active timers\n'
    message += '+ !time <name>        - starts timer for a certain boss\n'
    message += '+ !end <name>         - ends the timer for a certain boss\n'
    message += '+ !reset <name>       - restarts timer for a certain boss\n'
    message += '+ !set <name> <time>  - sets the timer for a boss manually\n'
    message += '```'
    await ctx.channel.send(message)
    return

@bot.command(name='soon')
async def getStatus(ctx):
    status = '>>> **Active timers:**\n'
    for key, value in bosstimers.items():
        if value > 0:
            status += f'```ini\n[{key:<20}{printTime(value)}]\n```'
    await ctx.channel.send(status)
    return

@bot.command(name='names')
async def getNames(ctx):
    names = '>>> **Available bosses:**\n'
    names += '```diff\n'
    for key in bosstimers.keys():
        names += f'- {key}\n'
    names += '```'
    await ctx.channel.send(names)
    return

@bot.command(name='reset')
async def restartTimer(ctx, name):
    name = name.strip().lower()
    if name not in bosstimers.keys():
        await ctx.channel.send(f'> {name} is not a valid boss name. Type "!names" to list all valid names.')
        return
    bosstimers[name] = float(bossinfo[name] * 60000)
    timerRunning[name] = True
    timestamp = time.time() * 1000

    await ctx.channel.send(f'>>> :alarm_clock: The timer for {name} has been restarted.\n```ini\n[{name:<20}{printTime(bosstimers[name])}]\n```')

    while bosstimers[name] > 0:
        await asyncio.sleep(1)
        bosstimers[name] -= time.time() * 1000 - timestamp
        timestamp = time.time() * 1000

        if bosstimers[name] <= 300000 and timerRunning[name]:  # 5-Minuten-Erinnerung
            channel = discord.utils.get(ctx.guild.channels, name="boss-timer")
            if channel:
                await channel.send(f"@everyone :alarm_clock: Reminder! Only 5 minutes left until **{name}** is due!")
            break

    if bosstimers[name] > -10000000:
        channel = discord.utils.get(ctx.guild.channels, name="boss-timer")
        if channel:
            await channel.send(f"@everyone :crossed_swords: **{name} is due!**".upper())
    timerRunning[name] = False
    return

@bot.command(name='end')
async def endTimer(ctx, name):
    name = name.strip().lower()

    if name not in bosstimers.keys():
        await ctx.channel.send(f'> {name} is not a valid boss name. Type "!names" to list all valid names.')
        return

    bosstimers[name] = -10000000
    await ctx.channel.send(f'> Timer for {name} was terminated manually.')
    return

@bot.command(name='time')
async def startTimer(ctx, name):
    name = name.strip().lower()

    if name not in bosstimers.keys():
        await ctx.channel.send(f'> {name} is not a valid boss name. Type "!names" to list all valid names.')
        return

    if timerRunning[name]:
        await ctx.channel.send(f'>>> :alarm_clock: Timer is already running.\n```ini\n[{name:<20}{printTime(bosstimers[name])}]\n```')
        return
    
    timerRunning[name] = True
    bosstimers[name] = float(bossinfo[name] * 60000)
    timestamp = time.time() * 1000

    await ctx.channel.send(f'>>> :alarm_clock: Timer started successfully.\n```ini\n[{name:<20}{printTime(bosstimers[name])}]\n```')

    while bosstimers[name] > 0:
        await asyncio.sleep(1)
        bosstimers[name] -= time.time() * 1000 - timestamp
        timestamp = time.time() * 1000

        if bosstimers[name] <= 300000 and timerRunning[name]:  # 5-Minuten-Erinnerung
            channel = discord.utils.get(ctx.guild.channels, name="boss-timer")
            if channel:
                await channel.send(f"@everyone :alarm_clock: Reminder! Only 5 minutes left until **{name}** is due!")
            break

    if bosstimers[name] > -10000000:
        channel = discord.utils.get(ctx.guild.channels, name="boss-timer")
        if channel:
            await channel.send(f"@everyone :crossed_swords: **{name} is due!**".upper())
    timerRunning[name] = False
    return

@bot.command(name='set')
async def setTimer(ctx, name, minutes: int):
    name = name.strip().lower()

    if name not in bosstimers.keys():
        await ctx.channel.send(f'> {name} is not a valid boss name. Type "!names" to list all valid names.')
        return

    bosstimers[name] = minutes * 60000
    timerRunning[name] = True
    timestamp = time.time() * 1000

    await ctx.channel.send(f'>>> :alarm_clock: Timer for {name} manually set to {minutes} minutes.\n```ini\n[{name:<20}{printTime(bosstimers[name])}]\n```')

    while bosstimers[name] > 0:
        await asyncio.sleep(1)
        bosstimers[name] -= time.time() * 1000 - timestamp
        timestamp = time.time() * 1000

        if bosstimers[name] <= 300000 and timerRunning[name]:  # 5-Minuten-Erinnerung
            channel = discord.utils.get(ctx.guild.channels, name="boss-timer")
            if channel:
                await channel.send(f"@everyone :alarm_clock: Reminder! Only 5 minutes left until **{name}** is due!")
            break

    if bosstimers[name] <= 0:
        channel = discord.utils.get(ctx.guild.channels, name="boss-timer")
        if channel:
            await channel.send(f"@everyone :crossed_swords: **{name} is due!**".upper())
    timerRunning[name] = False
    return

def printTime(millis):
    hours = math.floor(millis / 3600000)
    minutes = math.floor((millis % 3600000) / 60000)
    seconds = math.floor((millis % 60000) / 1000)
    return '{0:02d}:{1:02d}:{2:02d}'.format(hours, minutes, seconds)

keep_alive()
bot.run(TOKEN)