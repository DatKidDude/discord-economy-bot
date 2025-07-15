import discord
from discord.ext import commands
from database import Database
from random import choice
import logging
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN", "None")

db = Database()

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    if bot.user:
        print(f"We are ready to go in, {bot.user.name}")
    else:
        print("Something went wrong went starting up the bot")


@bot.event
async def on_member_join(member):

    users = db.get_users()
    # check if user is already in the database
    for user in users:
        if user[0] == member.id:
            print(f"{member.id} already exists")
            return
    
    db.add_user(member.id)

    for channel in member.guild.text_channels:
        if str(channel) == "general":
            await channel.send(f"{member.mention} has been awarded $1000 for joining beamconomy!")


@bot.command()
async def work(ctx):
    jobs = {
        "cleaned porta potties": 100,
        "commentatated for derby": 600,
        "won a derby": 1000,
        "sold merchandise": 300,
        "worked pit crew": 500,
        "watered the track": 100,
        "worked the food stand": 200,
        "worked the entrance": 600,
        "worked security detail": 400,
        "cleaned the cars": 700
    }

    user = ctx.author
    job, amount = choice(list(jobs.items()))

    try:
        db.update_currency(discord_id=user.id, amount=amount)
    except Exception as e:
        print(f"Error updating currency: {e}")
        await ctx.send("Something went wrong while working. Please try again.")
    else:   
        await ctx.send(f"{user} {job}: ${amount}")


@bot.command()
async def currency(ctx):
    user = ctx.author 
    try:
        amount = db.get_currency(discord_id=user.id)
    except Exception as e:
        print(f"Error retrieving currency from user: {e}")
        await ctx.send("Something went wrong while retrieving currency. Please try again.")
    else:
        await ctx.send(f"{user.mention} has ${amount}")
            
# Ensure TOKEN is always a string to satisfy bot.run(),
# since os.getenv() can return None if the env variable is missing.
# Providing a default None string avoids linter/type checker warnings.
try:
    bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)
except discord.errors.LoginFailure as e:
    print(f"A login error occurred: {e}")
finally:
    print("Closing application")