from flask import Flask
app = Flask(__name__)
@app.route("/")
def hello():
    return "Hello, World!"

import discord
from discord import app_commands
from discord.ext import commands
import datetime, asyncio
import pytz
import draw
import requests
import dotenv
import os
from threading import Thread
import numpy as np
import random

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
CHANNEL = 1276421499388956716
channel = None
# tz = zoneinfo.ZoneInfo("America/Los_Angeles")
tz = pytz.timezone("America/Los_Angeles")

def monthMap(m):
    return ((m + 3) % 12) + 2

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
    channel = client.get_channel(CHANNEL)
    client.loop.create_task(daily_message_task())
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.streaming, url="https://www.twitch.tv/advikg_", name="/help"))

size = 9
mines = 20
flags = 20
gamesWon = 1
totalGames = 1 #technically not accurate but i dont really care
offsets = [-1, 0, 1]
minesweep = None       
activeBoard = None      
boardID = None
isBoardNew = True
canPlay = True
letter_emoji = {
    0: "🅾️",
    1: "🇦\u200B", 2: "🇧\u200B", 3: "🇨\u200B", 4: "🇩\u200B",
    5: "🇪\u200B", 6: "🇫\u200B", 7: "🇬\u200B", 8: "🇭\u200B",
    9: "🇮\u200B",
    -1: "💥"
}
number_emoji = {
    0: "▫️",
    1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣",
    5: "5️⃣", 6: "6️⃣", 7: "7️⃣", 8: "8️⃣",
    9: "▫️", 10:"🚩", 11:"❌",
    -1: "💥"
}

@client.tree.command(name="setgames", guild=brogreID)
async def hitCommand(interaction: discord.Interaction, totalgames: int, wongames: int):
    if(interaction.user.id != 636737365125365810):
            await interaction.response.send_message("nah",ephemeral=True)
            return
    global totalGames, gamesWon
    totalGames = totalgames
    gamesWon = wongames
    await interaction.response.send_message("ok",ephemeral=True)

async def generateBoard(first_x, first_y):
    global minesweep, activeBoard, isBoardNew, flags, canPlay

    flags = 20
    isBoardNew = False
    canPlay = True
    minesweep[:] = 0
    safe = set()
    for dy in offsets:
        for dx in offsets:
            ny = first_y + dy
            nx = first_x + dx
            if 0 <= ny < size and 0 <= nx < size:
                safe.add((ny, nx))

    placed = 0
    while placed < mines:
        x = random.randrange(size)
        y = random.randrange(size)

        if (y, x) in safe or minesweep[y][x] == -1:
            continue

        minesweep[y][x] = -1
        placed += 1

    for a in offsets:
        for b in offsets:
            await hit(first_x+b,first_y+a,False)
    await displayBoard()

async def displayBoard(isGen=False):
    global activeBoard, boardID, channel, gamesWon, totalGames, canPlay

    disp = np.full((size + 1, size + 1), "⬜", dtype=object)

    for i in range(1, size + 1):
        disp[0, i] = letter_emoji.get(i, str(i))
        disp[i, 0] = letter_emoji.get(i, str(i))

    disp[0, 0] = letter_emoji[0]

    for y in range(size):
        for x in range(size):
            val = activeBoard[y, x]
            if val != 0:
                disp[y + 1, x + 1] = number_emoji.get(val, str(val))

    board_text = f"🚩:{flags}          Win Rate: {100*(gamesWon/totalGames):.2f}% ({gamesWon}/{totalGames})\n" + '\n'.join(''.join(row) for row in disp)

    if isGen:
        boardID = (await channel.send(board_text)).id
        return

    if(hasWon()):
        await channel.send("Severe W")
        gamesWon += 1
        totalGames += 1
        canPlay = False
    
    msg = await channel.fetch_message(boardID)
    await msg.edit(content= board_text)

@client.tree.command(name="sendboard", guild=brogreID)
async def start(interaction: discord.Interaction):
    if(interaction.user.id != 636737365125365810):
            await interaction.response.send_message("nah",ephemeral=True)
            return
    global minesweep, activeBoard, boardID, channel, isBoardNew,flags, canPlay
    flags = 20
    isBoardNew = False
    canPlay = True

    channel = client.get_channel(CHANNEL)
    minesweep = np.zeros((size, size), dtype=int)
    activeBoard = minesweep.copy()
    isBoardNew = True

    await displayBoard(True)
    await interaction.response.send_message("created board", ephemeral=True)

async def hit(x,y,shouldDisplay=True,user=None):
    global isBoardNew, minesweep, activeBoard, canPlay, totalGames

    if(canPlay == False):
        return

    if not (0 <= x < size and 0 <= y < size):
        return
    
    if(activeBoard[y][x] == 10):
        return

    if isBoardNew:
        await generateBoard(x, y)

    if minesweep[y][x] == -1:
        activeBoard[y][x] = -1
        await channel.send(f"{user.mention} done blew everyone up")
        canPlay = False
        totalGames += 1
        for i in range(size):
            for j in range(size):
                if(activeBoard[i][j] == 10 and minesweep[i][j] != -1):
                    activeBoard[i][j]=11
                if(minesweep[i][j] == -1):
                    activeBoard[i][j] = -1
                
        await displayBoard()
        return

    count = 0
    for dy in offsets:
        for dx in offsets:
            ny = y + dy
            nx = x + dx
            if 0 <= ny < size and 0 <= nx < size:
                if minesweep[ny][nx] == -1:
                    count += 1

    if activeBoard[y][x] != 0:
        return

    activeBoard[y][x] = count
    if(count == 0):
        activeBoard[y][x] = 9

    if count == 0:
        for dy in offsets:
            for dx in offsets:
                if dx == 0 and dy == 0:
                    continue

                ny = y + dy
                nx = x + dx

                if 0 <= ny < size and 0 <= nx < size:
                    if minesweep[ny][nx] != -1:
                        await hit(nx, ny, False)
    if (shouldDisplay):
        await displayBoard()
        

@client.tree.command(name="hit", guild=brogreID)
async def hitCommand(interaction: discord.Interaction, x: str, y: str):
    x = ord(x.lower()) - 97
    y = ord(y.lower()) - 97
    await hit(x,y,user=interaction.user)
    await interaction.response.defer()
    await interaction.delete_original_response()

@client.tree.command(name="flag", guild=brogreID)
async def flagCommand(interaction: discord.Interaction, x: str, y: str):
    global flags
    global canPlay
    if(canPlay == False):
        return
    x = ord(x.lower()) - 97
    y = ord(y.lower()) - 97
    if(activeBoard[y][x] == 0):
        activeBoard[y][x]=10
        flags -= 1
    elif(activeBoard[y][x] == 10):
        activeBoard[y][x] = 0
        flags += 1
    
    await displayBoard()
    await interaction.response.defer()
    await interaction.delete_original_response()

@client.tree.command(name="chord", guild=brogreID)
async def chordCommand(interaction: discord.Interaction, x: str, y: str):
    global flags
    x = ord(x.lower()) - 97
    y = ord(y.lower()) - 97
    if(activeBoard[y][x] == 10):
        return
    
    # technically its more optimal to just save the board state and then revert it if the flag check fails but i am REALLY lazy
    flagCount = 0
    for a in offsets:
        for b in offsets:
            if(a == 0 and b == 0):
                continue
            if not (0 <= x+b < size and 0 <= y+a < size):
                continue
            if(activeBoard[y+a][x+b] == 10):
                flagCount += 1

    if (flagCount != activeBoard[y][x]):
        await interaction.response.defer()
        await interaction.delete_original_response()
        return

    for a in offsets:
        for b in offsets:
            await hit(x+b,y+a,False,user=interaction.user)
    
    await displayBoard()
    await interaction.response.defer()
    await interaction.delete_original_response()

def hasWon():
    arr2 = np.array(activeBoard.copy())
    arr2 = np.where((arr2 == 0) | (arr2 == 10), -1, 0)
    return np.array_equal(np.array(minesweep), arr2)

async def daily_message_task():
    global minesweep, activeBoard, boardID, channel, isBoardNew,flags, canPlay
    global lastKnownMessageID
    await client.wait_until_ready()
    while not client.is_closed():
        now = datetime.datetime.now(tz)
        #15:35 = 3:35
        target = now.replace(hour=15, minute=35, second=0, microsecond=0)
        
        if target <= now:
            target += datetime.timedelta(days=1)
        while target.weekday() >= 5: #5sat 6sun
            target += datetime.timedelta(days=1)
        wait_time = (target - now).total_seconds()
        await asyncio.sleep(wait_time)
        clearArr()
        picture = None
        with open('calendar.png', 'rb') as f:
            picture = discord.File(f)
        lastKnownMessageID = (await channel.send(generateMessage(),file=picture,allowed_mentions=discord.AllowedMentions(roles=True))).id
        flags = 20
        isBoardNew = False
        canPlay = True
        minesweep = np.zeros((size, size), dtype=int)
        activeBoard = minesweep.copy()
        isBoardNew = True

        await displayBoard(True)

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

@client.tree.command(name="adminresetid",guild=brogreID)
async def adminresetid(interaction: discord.Interaction, boardid:str):
        global lastKnownMessageID
        if(interaction.user.id != 636737365125365810 or not boardid.isdigit()):
            await interaction.response.send_message("nah",ephemeral=True)
            return
        lastKnownMessageID = int(boardid)
        await interaction.response.send_message("set id",ephemeral=True)

@client.tree.command(name="adminprint",guild=brogreID)
async def adminprint(interaction: discord.Interaction):
        global lastKnownMessageID
        if(interaction.user.id != 636737365125365810):
            await interaction.response.send_message("nah",ephemeral=True)
            return
        clearArr()
        picture = None
        with open('calendar.png', 'rb') as f:
            picture = discord.File(f)
        lastKnownMessageID = (await interaction.response.send_message(generateMessage(),file=picture,allowed_mentions=discord.AllowedMentions(roles=True))).message_id

@client.tree.command(name="roletoggle",guild=brogreID)
async def roletoggle(interaction: discord.Interaction):
    user = interaction.user
    cdRole = interaction.guild.get_role(1418383855806713921)
    if(user.get_role(1418383855806713921)):
        await user.remove_roles(cdRole)
        await interaction.response.send_message("Removed Role",ephemeral=True)
        return
    await user.add_roles(cdRole)
    await interaction.response.send_message("Gave Role",ephemeral=True)

@client.tree.command(name="help",guild=brogreID)
async def help(interaction: discord.Interaction):
        await interaction.response.send_message("/add to add text \n /edit to edit a text (0 based index so if there are 3 messages on 3 lines a b c /edit 1 accesses b) \n /delete same story as edit \n /setimage to draw on the calendar \n /roletoggle get or remove the senior countdown role \n /hit to break on the minesweeper board \n /chord to chord on minesweeper \n /flag to flag on minesweeper",ephemeral=True)

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

@client.tree.command(name="whattimeisit",guild=brogreID)
async def whattimeisit(interaction: discord.Interaction):
    await interaction.response.send_message(datetime.datetime.now(tz))

@client.tree.command(name="resetcalendar",guild=brogreID)
async def reset(interaction:discord.Interaction):
    draw.resetCalendar()
    await interaction.response.send_message("Reset The Calendar")

async def editMsg():
    global lastKnownMessageID
    msg = await channel.fetch_message(lastKnownMessageID)
    await msg.edit(content=generateMessage(),allowed_mentions=discord.AllowedMentions(roles=True))

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
    now = datetime.datetime.now(tz)
    month = monthMap(now.month)
    week = weekOfMonth(now.date())
    day = now.weekday()+1

    Title = f"<@&1418383855806713921>\n# 🎓The Countdown🎓\n## Part: {month} Act: {week} Scene: {day}\n **Day: {(now.date()-schoolEpoch).days}/296 ({((now.date()-schoolEpoch).days)/2.96:.2f}%)**"
    Announce = "\n## Announcements"
    annMsg = genBullet(annArr)
    Today = "\n## Today's Events"
    todMsg = genBullet(todArr)
    Upcoming = "\n## Upcoming Events"
    upMsg = genBullet(upcon)
    Trivia = "\n## Trivia"
    tMsg = genBullet(trivArr)
    helpremark = "\n use /help to edit the board"
    draw.markCalendar(now.month,week,day)
    return Title + Announce + annMsg + Today + todMsg+ Upcoming + upMsg + Trivia +tMsg + helpremark

def run_flask():
    app.run(host="0.0.0.0", port=8000)

flask_thread = Thread(target=run_flask)
flask_thread.start()

client.run(token)