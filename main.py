# main.py - FULLY FIXED + ALL COMMANDS
import os
import asyncio
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
from youtube_search import YoutubeSearch
import tgcalls

# CONFIG (ENV SE LE RAHA HAI)
API_ID = int(os.getenv("API_ID", "36032857"))
API_HASH = os.getenv("API_HASH", "1335484542da44312a4e861ad7e41e32")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8483486360:AAEyV4U9D2nq1GC1QK1unuy-SpQImJMpdLE")

app = Client("vc_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
calls = PyTgCalls(app)

# QUEUE SYSTEM
queue = {}
current_song = {}

# PLAY FUNCTION
async def play_song(chat_id, query, user):
    global current_song
    msg = await app.send_message(chat_id, f"**SEARCHING...** MUSIC\n\n`{query}`")
    
    # Search YouTube
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        url = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]['title']
        thumb = results[0]['thumbnails'][0]
    except:
        return await msg.edit("**SONG NOT FOUND!**")

    # Auto Join VC
    try:
        await calls.join_group_call(chat_id, AudioPiped("https://bit.ly/3z8fY2x"))
    except: pass

    # Download
    file = f"{chat_id}.mp3"
    ydl_opts = {
        'format': 'bestaudio',
        'outtmpl': file,
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}]
    }
    try:
        yt_dlp.YoutubeDL(ydl_opts).download([url])
    except:
        return await msg.edit("**DOWNLOAD FAILED!**")

    # Play
    await calls.change_stream(chat_id, AudioPiped(file, volume=200))
    current_song[chat_id] = {"title": title, "user": user, "file": file}

    # Buttons
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("⏸ PAUSE", "pause"), InlineKeyboardButton("▶ RESUME", "resume")],
        [InlineKeyboardButton("⏭ SKIP", "skip"), InlineKeyboardButton("⏹ STOP", "stop")]
    ])

    await msg.edit(
        f"**NOW PLAYING** MUSIC\n\n**{title}**\n\nRequested by: @{user}\n\nBot by @ahamsharma578",
        reply_markup=buttons
    )

# /play
@app.on_message(filters.command("play") & filters.group)
async def play(_, m: Message):
    if len(m.command) < 2:
        return await m.reply("**/play perfect**")
    query = " ".join(m.command[1:])
    user = m.from_user.username or m.from_user.first_name
    asyncio.create_task(play_song(m.chat.id, query, user))

# /pause
@app.on_message(filters.command("pause") & filters.group)
async def pause(_, m: Message):
    try:
        await calls.pause_stream(m.chat.id)
        await m.reply("**PAUSED** MUSIC")
    except:
        await m.reply("**NOTHING PLAYING!**")

# /resume
@app.on_message(filters.command("resume") & filters.group)
async def resume(_, m: Message):
    try:
        await calls.resume_stream(m.chat.id)
        await m.reply("**RESUMED** MUSIC")
    except:
        await m.reply("**NOTHING PAUSED!**")

# /skip
@app.on_message(filters.command("skip") & filters.group)
async def skip(_, m: Message):
    try:
        await calls.change_stream(m.chat.id, None)
        await m.reply("**SKIPPED** MUSIC")
    except:
        await m.reply("**NOTHING TO SKIP!**")

# /stop
@app.on_message(filters.command("stop") & filters.group)
async def stop(_, m: Message):
    try:
        await calls.leave_group_call(m.chat.id)
        await m.reply("**STOPPED + LEFT VC** MUSIC")
    except:
        await m.reply("**NOT IN VC!**")

# /queue
@app.on_message(filters.command("queue") & filters.group)
async def queue_cmd(_, m: Message):
    if m.chat.id not in current_song:
        return await m.reply("**QUEUE EMPTY!**")
    song = current_song[m.chat.id]
    await m.reply(f"**QUEUE:**\n\n1. {song['title']}\nRequested by: @{song['user']}")

# /volume
@app.on_message(filters.command("volume") & filters.group)
async def volume(_, m: Message):
    if len(m.command) < 2:
        return await m.reply("**/volume 150**")
    try:
        vol = int(m.command[1])
        if 1 <= vol <= 200:
            await calls.change_volume_call(m.chat.id, vol)
            await m.reply(f"**VOLUME SET TO {vol}%**")
        else:
            await m.reply("**VOLUME 1-200 ONLY!**")
    except:
        await m.reply("**INVALID VOLUME!**")

# /seek
@app.on_message(filters.command("seek") & filters.group)
async def seek(_, m: Message):
    if len(m.command) < 2:
        return await m.reply("**/seek 10** or **/seek -10**")
    try:
        sec = int(m.command[1])
        await calls.seek_stream(m.chat.id, sec)
        await m.reply(f"**SEEKED {sec} SEC**")
    except:
        await m.reply("**INVALID SEEK!**")

# /start
@app.on_message(filters.command("start"))
async def start(_, m: Message):
    await m.reply(
        "**AUTO VC BOT LIVE!** MUSIC\n\n"
        "**COMMANDS:**\n"
        "`/play perfect` - Play song\n"
        "`/pause` - Pause\n"
        "`/resume` - Resume\n"
        "`/skip` - Next\n"
        "`/stop` - Stop + Leave\n"
        "`/queue` - Show queue\n"
        "`/volume 150` - Set volume\n"
        "`/seek 10` - Forward 10 sec\n"
        "`/seek -10` - Backward 10 sec\n\n"
        "Bot by @ahamsharma578"
    )

print("BOT LIVE! MUSIC")
app.run()
asyncio.run(calls.start())
