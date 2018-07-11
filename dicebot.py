#!/usr/bin/env python3

import random
import sys

import discord
from discord.ext import commands

description = "Dice rolling bot"""

bot = commands.Bot(command_prefix="/", description=description)

@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")


def roll_inner(cmd : str):
    dice, sides = map(int, cmd.split("d"))
    rolls = [random.randint(1, sides) for r in range(dice)]
    if rolls:
        result = " + ".join(map(str, rolls)) + " = %d" % sum(rolls)
    else:
        result = ""
    return result


@bot.command()
async def roll(cmd : str):
    """Rolls dice in roll20 format."""
    try:
        result = roll_inner(cmd)
    except Exception:
        await bot.say("invalid format")
        return
    await bot.say(result)


# Give token on command line
# https://discordapp.com/developers/applications/me to find it
if __name__ == "__main__":
    if len(sys.argv) > 1:
        bot.run(sys.argv[1])
    else:
        print("Must give Discord bot token on command line")
