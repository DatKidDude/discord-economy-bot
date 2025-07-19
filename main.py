import discord
from discord.ext import commands
from database import Database
from random import choice
from datetime import datetime, timezone, timedelta
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

def user_exists(user_id):
    """Returns True if the user exists in the database
    else returns False"""
    users = db.get_all_users()

    for user in users:
        if user[0] == user_id:
            return True 
        
    return False
    

@bot.command()
async def remove(ctx): # Only used for development
    """Deletes all messages in a channel"""
    user = ctx.author

    deleted = await ctx.channel.purge(limit=1000) 
    await ctx.send(f"Deleted {len(deleted)} messages")

@bot.event
async def on_ready():
    if bot.user:
        print(f"We are ready to go in, {bot.user.name}")
    else:
        print("Something went wrong went starting up the bot")

@bot.command()
async def join(ctx):
    """Adds the user to the database"""
    user = ctx.author 
    user_id = user.id

    if (user_exists(user_id=user_id)):
        await ctx.send(f"{user.mention} is already active")
        return
    
    try:
        db.add_user(user_id)
    except Exception as e:
        print(f"Error occurred while adding user to database: {e}")
    else:
        await ctx.send(f"{user.mention} has been awarded $1000 for joining beamconomy!")
 

# @bot.event
# async def on_member_join(member):

#     users = db.get_all_users()
#     # check if user is already in the database
#     for user in users:
#         if user[0] == member.id:
#             print(f"{member.id} already exists")
#             return
    
#     db.add_user(member.id)

#     for channel in member.guild.text_channels:
#         if str(channel) == "general":
#             await channel.send(f"{member.mention} has been awarded $1000 for joining beamconomy!")

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
    user_id = user.id
    
    _, _, cooldown_time_utc = db.get_user(user_id)

    current_time_utc = datetime.now(timezone.utc)

    # The default database `event_time` value is NULL 
    # User is only allowed to run the command every 24 hours
    if cooldown_time_utc is None or current_time_utc >= cooldown_time_utc:
        job, amount = choice(list(jobs.items()))
        try:
            tomorrow_utc = datetime.now(timezone.utc) + timedelta(hours=24)
            db.update_currency(discord_id=user.id, currency=amount, event_time=tomorrow_utc)
        except Exception as e:
            print(f"Error updating currency: {e}")
            await ctx.send("Something went wrong while working. Please try again.")
        else:   
            await ctx.send(f"{user} {job}: ${amount}")
    else:
        cooldown = cooldown_time_utc - current_time_utc # returns a timedelta object
        hour = cooldown.seconds // 3600   
        minutes = (cooldown.seconds // 60) % 60
        await ctx.send(f"{user.mention} must wait {hour}:{minutes:02} before working again")


@bot.command()
async def currency(ctx):
    user = ctx.author 
    user_id = user.id

    try:
        amount = db.get_currency(discord_id=user_id)
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