import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os

TOKEN = os.getenv("DISCORD_TOKEN")   # Railway will provide this
VIDEO_URL = "https://www.youtube.com/watch?v=jiTV8MwgL3c"

YDL_OPTS = {
    'format': 'bestaudio/best',
    'outtmpl': 'boiling.%(ext)s',
    'quiet': True,
    'no_warnings': True,
}

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

def download_audio():
    if os.path.exists("boiling.webm") or os.path.exists("boiling.m4a"):
        return
    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        ydl.download([VIDEO_URL])

async def play_loop(voice_client):
    path = None
    for ext in ['webm', 'm4a', 'opus']:
        p = f"boiling.{ext}"
        if os.path.exists(p):
            path = p
            break
    if not path:
        return

    def after_play(error):
        if error:
            print(error)
        if voice_client.is_connected():
            asyncio.run_coroutine_threadsafe(play_loop(voice_client), bot.loop)

    voice_client.play(discord.FFmpegPCMAudio(path), after=after_play)

@bot.command(name="setup")
async def setup(ctx):
    if not ctx.author.voice:
        return await ctx.send("❌ Join a voice channel first.")
    await ctx.send("🔽 Preparing boiling sounds...")
    await bot.loop.run_in_executor(None, download_audio)
    voice = ctx.voice_client or await ctx.author.voice.channel.connect()
    await ctx.send(f"🔊 Boiling forever in **{voice.channel.name}**!")
    await play_loop(voice)

@bot.command(name="stop")
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

bot.run(TOKEN)
