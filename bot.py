import discord
from discord.ext import commands
import asyncio
import os

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def play_loop(voice_client):
    """Loop the local boiling.mp3 file forever."""
    if not os.path.exists("boiling.mp3"):
        return

    def after_play(error):
        if error:
            print(f"Playback error: {error}")
        if voice_client.is_connected():
            asyncio.run_coroutine_threadsafe(play_loop(voice_client), bot.loop)

    voice_client.play(discord.FFmpegPCMAudio("boiling.mp3"), after=after_play)

@bot.command(name="setup")
async def setup(ctx):
    if not ctx.author.voice:
        return await ctx.send("❌ Join a voice channel first.")

    voice = ctx.voice_client or await ctx.author.voice.channel.connect()
    await ctx.send(f"🔊 Boiling forever in **{voice.channel.name}**!")
    await play_loop(voice)

@bot.command(name="stop")
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

bot.run(TOKEN)
