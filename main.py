from flask import Flask
app = Flask(__name__)
@app.route("/")
def hello():
    return "Hello, World!"



import discord
from discord import app_commands
from discord.ext import commands
from discord.ext import commands #idk how important this one is
import datetime, asyncio
import pytz
import draw
import requests
import dotenv
import os

dotenv.load_dotenv()

intents = discord.Intents.all()
token = os.getenv("TOKEN")

annArr = []
todArr = []
upcon = []
trivArr = []

client = commands.Bot(command_prefix="cd", intents=intents)
# primary = "1276421499388956716"
# testing channel 1362542120291799070
CHANNEL = 1362542120291799070
channel = client.get_channel(CHANNEL)
# tz = zoneinfo.ZoneInfo("America/Los_Angeles")
tz = pytz.timezone("America/Los_Angeles")

monthDict = {
    9:2,
    10:3,
    11:4,
    12:5,
    1:6,
    2:7,
    3:8,
    4:9,
    5:10,
    6:11
}

schoolEpoch = datetime.date(2025,8,12)
brogreID = discord.Object(id=915051802276294676)
lastKnownMessageID = None

def downloadPicture(url):
    data = requests.get(url).content
    f = open('calendar.png','wb')
    f.write(data)
    f.close()

@client.event
async def on_ready():
    global channel
    await client.tree.sync(guild=brogreID)
    client.loop.create_task(daily_message_task())
    channel = client.get_channel(CHANNEL)

async def daily_message_task():
    global lastKnownMessageID
    await client.wait_until_ready()
    while not client.is_closed():
        now = datetime.datetime.now(tz)
        #15:35 = 3:35
        target = now.replace(hour=22, minute=11, second=0, microsecond=0)
        if target <= now:
            target += datetime.timedelta(days=1)
        wait_time = (target - now).total_seconds()
        await asyncio.sleep(wait_time)
        clearArr()
        picture = None
        with open('calendar.png', 'rb') as f:
            picture = discord.File(f)
        f.close()
        lastKnownMessageID = (await channel.send(generateMessage(),file=picture)).id

@client.tree.command(name="add",guild=brogreID)
@app_commands.describe(section="Section")
@app_commands.choices(section=[
        app_commands.Choice(name="Announcements", value="ann"),
        app_commands.Choice(name="Today", value="tod"),
        app_commands.Choice(name="Upcoming", value="upc"),
        app_commands.Choice(name="Trivia", value="triv")
    ])
async def add(interaction: discord.Interaction, section:str, arg:str):
    global annArr 
    global todArr 
    global upcon 
    global trivArr  
    match section:
        case "ann":
            annArr.append(arg)
        case "tod":
            todArr.append(arg)
        case "upc":
            upcon.append(arg)
        case "triv":
            trivArr.append(arg)
        case _:
            await interaction.response.send_message(f"no",ephemeral=True)
            return
    await editMsg()
    await interaction.response.send_message(f"Added",ephemeral=True)

@client.tree.command(name="delete",guild=brogreID)
@app_commands.describe(section="Section")
@app_commands.choices(section=[
        app_commands.Choice(name="Announcements", value="ann"),
        app_commands.Choice(name="Today", value="tod"),
        app_commands.Choice(name="Upcoming", value="upc"),
        app_commands.Choice(name="Trivia", value="triv")
    ])
async def delete(interaction: discord.Interaction, section:str, index:int):
    global annArr 
    global todArr 
    global upcon 
    global trivArr  
    match section:
        case "ann":
            del annArr[index]
        case "tod":
            del todArr[index]
        case "upc":
            del upcon[index]
        case "triv":
            del trivArr[index]
        case _:
            await interaction.response.send_message(f"no",ephemeral=True)
            return
    await editMsg()
    await interaction.response.send_message(f"Deleted",ephemeral=True)

@client.tree.command(name="edit",guild=brogreID)
@app_commands.describe(section="Section")
@app_commands.choices(section=[
        app_commands.Choice(name="Announcements", value="ann"),
        app_commands.Choice(name="Today", value="tod"),
        app_commands.Choice(name="Upcoming", value="upc"),
        app_commands.Choice(name="Trivia", value="triv")
    ])
async def edit(interaction: discord.Interaction, section:str, index:int, newtext:str):
    global annArr 
    global todArr 
    global upcon 
    global trivArr  
    match section:
        case "ann":
            annArr[index] = newtext
        case "tod":
            todArr[index] = newtext
        case "upc":
            upcon[index] = newtext
        case "triv":
            trivArr[index] = newtext
        case _:
            await interaction.response.send_message(f"no",ephemeral=True)
            return
    await editMsg()
    await interaction.response.send_message(f"Edited",ephemeral=True)

@client.tree.command(name="setimage",guild=brogreID)
@app_commands.describe(image="attach")
async def setImage(interaction: discord.Interaction,image: discord.Attachment = None):
    embed = discord.Embed(title=f"New calendar picture set by @{interaction.user.name}")
    if image is None:
            await interaction.response.send_message("You think you sneaky, put an image", ephemeral=True)
            return
    if not image.content_type.startswith("image/"):
            await interaction.response.send_message("You think you sneaky, put an image", ephemeral=True)
            return
    embed.set_image(url=image.url)
    downloadPicture(image.url)
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="showimage",guild=brogreID)
async def showimage(interaction: discord.Interaction):
    with open('calendar.png', 'rb') as f:
            picture = discord.File(f)
            await interaction.response.send_message(file=picture)
    f.close()

@client.tree.command(name="resetcalendar",guild=brogreID)
async def reset(interaction:discord.Interaction):
    draw.resetCalendar()
    await interaction.response.send_message("Reset The Calendar")

async def editMsg():
    global lastKnownMessageID
    msg = await channel.fetch_message(lastKnownMessageID)
    await msg.edit(content=generateMessage())

def weekOfMonth(date):
    first_day_of_month = date.replace(day=1)
    adjusted_day = date.day + first_day_of_month.weekday()
    return (adjusted_day - 1) // 7 + 1

def genBullet(array):
    main = ""
    for i in array:
        main += f"\n - {i}"
    return main

def clearArr():
    global annArr 
    global todArr 
    global upcon 
    global trivArr  
    annArr = []
    todArr = []
    upcon = []
    trivArr = []

def generateMessage():
    global annArr 
    global todArr 
    global upcon 
    global trivArr  
    main = ""
    month = monthDict[datetime.datetime.now().month]
    week = weekOfMonth(datetime.datetime.today())
    day = datetime.datetime.today().weekday()+1
    Title = f"# The Countdown\n## Part: {month} Act: {week} Scene: {day}\n **Day: {(datetime.date.today()-schoolEpoch).days}/296 ({((datetime.date.today()-schoolEpoch).days)/2.96}%)**"
    Announce = "\n## Announcements"
    annMsg = genBullet(annArr)
    Today = "\n## Today's Events"
    todMsg = genBullet(todArr)
    Upcoming = "\n## Upcoming Events"
    upMsg = genBullet(upcon)
    Trivia = "\n## Trivia"
    tMsg = genBullet(trivArr)
    draw.markCalendar(datetime.datetime.now().month,week,day)
    return Title + Announce + annMsg + Today + todMsg+ Upcoming + upMsg + Trivia +tMsg

client.run(token)

app.run(host='0.0.0.0', port=8000)