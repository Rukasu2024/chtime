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
    #frozen
    "eye": 30,
    "swampi": 35,
    "woody": 40,
    "chain": 45,
    "grom": 50,
    "pyrus": 55,
    #dragonlord
    "150": 60,
    "155": 70,
    "160": 80,
    "165": 90,
    "170": 100,
    "180": 110,
    #exalted dragonlord
    "onyx": 60,
    "skath": 70,
    "gron": 80,
    "dobby": 90,
    "flappy": 100,
    "phantom": 110,
    "unox": 120,
    "prot": 130
}

bosstimers = {
    #frozen
    "eye": 0,
    "swampi": 0,
    "woody": 0,
    "chain": 0,
    "grom": 0,
    "pyrus": 0,
    #dragonlord
    "150": 0,
    "155": 0,
    "160": 0,
    "165": 0,
    "170": 0,
    "180": 0,
    #exalted dragonlord
    "onyx": 0,
    "skath": 0,
    "gron": 0,
    "dobby": 0,
    "flappy": 0,
    "phantom": 0,
    "unox": 0,
    "prot": 0
}

timerRunning = {
    #frozen
    "eye": False,
    "swampi": False,
    "woody": False,
    "chain": False,
    "grom": False,
    "pyrus": False,
    #dragonlord
    "150": False,
    "155": False,
    "160": False,
    "165": False,
    "170": False,
    "180": False,
    #exalted dragonlord
    "onyx": False,
    "skath": False,
    "gron": False,
    "dobby": False,
    "flappy": False,
    "phantom": False,
    "unox": False,
    "prot": False
}

TOKEN = os.getenv('TOKEN')

bot = commands.Bot(command_prefix='!ch', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}.')

@bot.event
async def on_command_error(ctx, error):
    await ctx.channel.send('>>> Oh oh! An Error occured o_o\n Did you maybe forget to enter the bossname?')
    return

@bot.command(name='info')
async def getInfo(ctx):
    message = '>>> **Available commands:**\n'
    message += '```diff\n'
    message += '+ !chnames           - lists the names of all available bosses\n'
    message += '+ !chstatus          - lists all active timers\n'
    message += '+ !chtime <name>     - starts timer for a certain boss\n'
    message += '+ !chend <name>      - ends the timer for a certain boss\n'
    message += '+ !chrestart <name>  - restarts timer for a certain boss\n'
    message += '```'
    await ctx.channel.send(message)
    return

@bot.command(name='status')
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
    for key, value in bosstimers.items():
            names += f'- {key}\n'
    names += '```'
    await ctx.channel.send(names)
    return

@bot.command(name='restart')
async def restartTimer(ctx, name):
    name = name.strip().lower()
    if name not in bosstimers.keys():
        await ctx.channel.send(f'> {name} is not a valid boss name. Type "!chnames" to list all valid names.')
        return
    if not timerRunning[name]:
      await startTimer(ctx, name)
      return
    bosstimers[name] = float(bossinfo[name] * 60000)
    await ctx.channel.send(f'>>> :alarm_clock: The timer for {name} has been restarted.\n```ini\n[{name:<20}{printTime(bosstimers[name])}]\n```')
    return

@bot.command(name='end')
async def endTimer(ctx, name):
    name = name.strip().lower()

    if name not in bosstimers.keys():
        await ctx.channel.send(f'> {name} is not a valid boss name. Type "!chtime names" to list all valid names.')
        return

    bosstimers[name] = -10000000
    await ctx.channel.send(f'> Timer for {name} was terminated manually.')
    return

@bot.command(name='time')
async def startTimer(ctx, name):
    name = name.strip().lower()

    if name not in bosstimers.keys():
        await ctx.channel.send(f'> {name} is not a valid boss name. Type "!chnames" to list all valid names.')
        return

    if timerRunning[name]:
        await ctx.channel.send(f'>>> :alarm_clock: Timer is already running.\n```ini\n[{name:<20}{printTime(bosstimers[name])}]\n```')
        return
    
    timerRunning[name] = True
    bosstimers[name] = float(bossinfo[name] * 60000)
    timestamp = time.time() * 1000

    await ctx.channel.send(f'>>> :alarm_clock: Timer started succesfully.\n```ini\n[{name:<20}{printTime(bosstimers[name])}]\n```')

    while bosstimers[name] > 0:
        await asyncio.sleep(1)
        bosstimers[name] -= time.time() * 1000 - timestamp
        timestamp = time.time() * 1000

    if bosstimers[name] > -10000000:
        await ctx.channel.send(':crossed_swords:' + f'**{name} is due!**'.upper())
    timerRunning[name] = False
    return

def printTime(millis):
        hours = math.floor(millis / 3600000)
        minutes = math.floor((millis % 3600000) / 60000)
        seconds = math.floor((millis % 60000) / 1000)
        return '{0:02d}:{1:02d}:{2:02d}'.format(hours, minutes, seconds)

keep_alive()
bot.run(TOKEN)
