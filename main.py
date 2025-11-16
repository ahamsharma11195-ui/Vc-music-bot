# main.py
import os
import asyncio
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
from youtube_search import YoutubeSearch

API_ID = 36032857
API_HASH = "1335484542da44312a4e861ad7e41e32"
BOT_TOKEN = "8483486360:AAEyV4U9D2nq1GC1QK1unuy-SpQImJMpdLE"

app = Client("vc_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
calls = PyTgCalls(app)

async def play_song(chat_id, query, user):
    msg = await app.send_message(chat_id, f"**VC START + SEARCHING...** MUSIC\n\n`{query}`")
    results = YoutubeSearch(query, max_results=1).to_dict()
    url = f"https://youtube.com{results[0]['url_suffix']}"
    title = results[0]['title']
    try:
        await calls.join_group_call(chat_id, AudioPiped("https://bit.ly/3z8fY2x"))
    except: pass
    file = f"{chat_id}.mp3"
    ydl_opts = {'format': 'bestaudio', 'outtmpl': file, 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}]}
    yt_dlp.YoutubeDL(ydl_opts).download([url])
    await calls.change_stream(chat_id, AudioPiped(file, volume=200))
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("PAUSE", "pause"), InlineKeyboardButton("RESUME", "resume")],
        [InlineKeyboardButton("SKIP", "skip"), InlineKeyboardButton("STOP", "stop")]
    ])
    await msg.edit(f"**PLAYING** MUSIC\n\n**{title}**\n\nRequested by: @{user}", reply_markup=buttons)

@app.on_message(filters.command("play") & filters.group)
async def play(_, m: Message):
    if len(m.command) < 2: return await m.reply("**/play perfect**")
    query = " ".join(m.command[1:])
    user = m.from_user.username or m.from_user.first_name
    asyncio.create_task(play_song(m.chat.id, query, user))

@app.on_message(filters.command("start"))
async def start(_, m: Message):
    await m.reply("**AUTO VC BOT LIVE!**\n`/play perfect` → VC khud start hoga!")

print("BOT LIVE!")
app.run()
asyncio.run(calls.start())
