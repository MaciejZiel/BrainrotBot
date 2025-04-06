import asyncio
import discord
from discord.ext import commands
import os
import random
from dotenv import load_dotenv
from discord import FFmpegPCMAudio, PCMVolumeTransformer
import time
import asyncio

play_start_time = None
load_dotenv()
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    print("❌ Nie załadowano tokenu bota! Sprawdź plik .env.")
    exit()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

SONGS_FOLDER = "Songs"
WOMP_SONG = os.path.join(SONGS_FOLDER, "WOMP.mp3")
EDGE_SONG = os.path.join(SONGS_FOLDER, "edge till it hurts (TAKE ME TO CHURCH HOZIER BRAIN ROT PARODY SONG LYRICS VIDEO).mp3")
MOONLIGHT_SONG = os.path.join(SONGS_FOLDER, "rizzing in the moonlight (DANCIN BRAIN ROT PARODY KRONO REMIX TIKTOK SONG).mp3")
BAYEROTA_SONG = os.path.join(SONGS_FOLDER, "Rota bayerota.mp3")
SKIBI_SONG = os.path.join(SONGS_FOLDER, "To Skibidi Or Not (feat. The Brainrot Opera).mp3")
BAYERKO_SONG = os.path.join(SONGS_FOLDER, "bayerko bayerko.mp3")
RIZZMAS_SONG = os.path.join(SONGS_FOLDER, "i don't gyatt a lot for chrizzmas (MARIAH CAREY ALL I GOT FOR CHRISTMAS IS YOU PARODY).mp3")
SKIBIDISZEWSKI_SONG = os.path.join(SONGS_FOLDER, "skbidiszewski.mp3")
OHIO_SONG = os.path.join(SONGS_FOLDER, "Let It Snow (Brainrot Edition) ＂Ohio, Ohio, Ohio＂ AI Parody cover (lyrics by notjewboi).mp3")
MANGO_SONG = os.path.join(SONGS_FOLDER, "MANGOS TIKTOK VERSION (PHONK).mp3")
ERIKA_SONG = os.path.join(SONGS_FOLDER, "Erika! [German  English Lyrics].mp3")
GYATPOKALIPSA_SONG = os.path.join(SONGS_FOLDER, "Gyatpokalipsa.mp3")
ODA_DO_GOONRZYNKA_SONG = os.path.join(SONGS_FOLDER, "Oda do guunrzynka.mp3")
SKIBIDI_BAYER_SONG = os.path.join(SONGS_FOLDER, "SKIBIDI BAYER (GRIMACE SHAKE REMIX).mp3")


queue = []
voice_client = None
is_paused = False
volume = 0.5


total_time_on_channel = 0

@bot.event
async def on_ready():
    print(f"Bot zalogowany jako {bot.user}")
    bot.loop.create_task(track_time_on_channel())

async def track_time_on_channel():
    global total_time_on_channel

    while True:
        await asyncio.sleep(1)

        if voice_client and voice_client.is_connected():
            total_time_on_channel += 1  # Dodaj 1 sekundę

            with open("../BrainrotBot/time_spent_on_channel.txt", "w") as f:
                minutes = total_time_on_channel // 60
                seconds = total_time_on_channel % 60
                f.write(f"Sumaryczny czas: {minutes:02}:{seconds:02}")

@bot.command(name="total_time")
async def total_time_playing(ctx):
    try:
        with open("../BrainrotBot/time_spent_on_channel.txt", "r") as f:
            time_data = f.read()
        await ctx.send(f"⏱️ {time_data}")
    except FileNotFoundError:
        await ctx.send("❌ Nie zarejestrowano jeszcze czasu na kanale.")

async def play_next(ctx):
    global voice_client, queue

    if queue:
        item = queue.pop(0)

        if os.path.exists(item):
            source = FFmpegPCMAudio(item, executable="C:\\ffmpeg-2024-11-28-git-bc991ca048-full_build\\bin\\ffmpeg.exe")
            source = PCMVolumeTransformer(source, volume)  # Ustawianie głośności na źródle audio
            voice_client.play(source, after=lambda e: bot.loop.create_task(after_playing(ctx, e)))
            await ctx.send(f"🎶 Odtwarzam: {os.path.basename(item)}")
        else:
            await ctx.send(f"❌ Plik nie istnieje: {item}")
            await play_next(ctx)
    else:
        await ctx.send("🎶 Kolejka zakończona. Brak więcej utworów.")

async def after_playing(ctx, e):
    if e:
        print(f"❌ Wystąpił błąd: {e}")
    await play_next(ctx)

@bot.command(name="volume")
async def volume_control(ctx, vol: float):
    global volume
    if 0.0 <= vol <= 1.0:
        volume = vol
        if voice_client and voice_client.is_playing():
            voice_client.source.volume = volume
        await ctx.send(f"🔊 Głośność ustawiona na {vol * 100}%")
    else:
        await ctx.send("❌ Proszę podać wartość w zakresie od 0.0 do 1.0.")

@bot.command(name="play")
async def play(ctx):
    global voice_client, queue

    if ctx.author.voice:
        channel = ctx.author.voice.channel
        voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

        if not voice_client:
            voice_client = await channel.connect()
        elif voice_client.channel != channel:
            await voice_client.move_to(channel)

        if not queue:
            for file in os.listdir(SONGS_FOLDER):
                if file.endswith(".mp3") or file.endswith(".wav"):
                    queue.append(os.path.join(SONGS_FOLDER, file))
            random.shuffle(queue)

        if queue:
            await play_next(ctx)
        else:
            await ctx.send("❌ Brak piosenek w folderze Songs.")
    else:
        await ctx.send("❌ Musisz być na kanale głosowym, aby rozpocząć odtwarzanie.")

@bot.command(name="skip")
async def skip(ctx):
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send("⏭️ Pominięto bieżący utwór.")
        await play_next(ctx)
    else:
        await ctx.send("❌ Bot nie odtwarza żadnego utworu.")

@bot.command(name="pause")
async def pause(ctx):
    global is_paused
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        is_paused = True
        await ctx.send("⏸️ Odtwarzanie zostało zatrzymane.")
    else:
        await ctx.send("❌ Bot nie odtwarzam żadnej muzyki.")

@bot.command(name="resume")
async def resume(ctx):
    global is_paused
    if voice_client and is_paused:
        voice_client.resume()
        is_paused = False
        await ctx.send("▶️ Wznowiono odtwarzanie muzyki.")
    else:
        await ctx.send("❌ Nie ma żadnej muzyki wstrzymanej do wznowienia.")

@bot.command(name="kys")
async def kys(ctx):
    global voice_client
    if voice_client:
        await voice_client.disconnect()
        await ctx.send("👋 Bot opuścił kanał głosowy.")
    else:
        await ctx.send("❌ Bot nie jest połączony z żadnym kanałem głosowym.")


@bot.command(name="erika")
async def erika(ctx):
    await play_song(ctx, ERIKA_SONG)

@bot.command(name="skibidiszewski")
async def skibidiszewski(ctx):
    await play_song(ctx, SKIBIDISZEWSKI_SONG)

@bot.command(name="mango")
async def mango(ctx):
    await play_song(ctx, MANGO_SONG)

@bot.command(name="rizzmas")
async def rizzmas(ctx):
    await play_song(ctx, RIZZMAS_SONG)

@bot.command(name="ohio")
async def rizzmas(ctx):
    await play_song(ctx, OHIO_SONG)

@bot.command(name="bayerko")
async def bayerko(ctx):
    await play_song(ctx, BAYERKO_SONG)

@bot.command(name="edge")
async def edge(ctx):
    await play_song(ctx, EDGE_SONG)

@bot.command(name="moonlight")
async def moonlight(ctx):
    await play_song(ctx, MOONLIGHT_SONG)

@bot.command(name="skibidi")
async def skibidi(ctx):
    await play_song(ctx, SKIBI_SONG)

@bot.command(name="bayerota")
async def bayerota(ctx):
    await play_song(ctx, BAYEROTA_SONG)

@bot.command(name="womp")
async def womp(ctx):
    await play_song(ctx, WOMP_SONG)

@bot.command(name="gyatpokalipsa")
async def gyatpokalipsa(ctx):
    await play_song(ctx, GYATPOKALIPSA_SONG)

@bot.command(name="oda")
async def oda(ctx):
    await play_song(ctx, ODA_DO_GOONRZYNKA_SONG)

@bot.command(name="skibidibayer")
async def skibidibayer(ctx):
    await play_song(ctx, SKIBIDI_BAYER_SONG)



async def play_song(ctx, song_path):
    global voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()

    if os.path.exists(song_path):
        source = FFmpegPCMAudio(song_path, executable="C:\\ffmpeg-2024-11-28-git-bc991ca048-full_build\\bin\\ffmpeg.exe")
        source = PCMVolumeTransformer(source, volume)  # Ustawianie głośności na źródle audio
        voice_client.play(source, after=lambda e: bot.loop.create_task(after_playing(ctx, e)))
        await ctx.send(f"🎶 Odtwarzam: {os.path.basename(song_path)}")
    else:
        await ctx.send("❌ Plik nie istnieje.")


@bot.command(name="commands")
async def commands_help(ctx):
    help_message = """
    🎶 **Dostępne komendy:**

    **!play** - Rozpoczyna odtwarzanie muzyki z folderu "Songs". Aby odtwarzać piosenki, musisz być na kanale głosowym.

    **!skip** - Pomija aktualnie odtwarzaną piosenkę.

    **!pause** - Wstrzymuje odtwarzanie muzyki.

    **!resume** - Wznawia wstrzymaną muzykę.

    **!volume <wartość>** - Ustawia głośność bota. Zakres od 0.0 do 1.0. Przykład: !volume 0.5

    **!kys** - Odłącza bota z kanału głosowego.

    **!bayerko, !edge, !moonlight, !skibidi, !bayerota** - Odtwarza różne utwory z folderu "Songs".

    """
    await ctx.send(help_message)




async def play_song(ctx, song_path):
    global voice_client, play_start_time
    if voice_client and voice_client.is_playing():
        voice_client.stop()

    if os.path.exists(song_path):
        source = FFmpegPCMAudio(song_path, executable="C:\\ffmpeg-2024-11-28-git-bc991ca048-full_build\\bin\\ffmpeg.exe")
        source = PCMVolumeTransformer(source, volume)
        voice_client.play(source, after=lambda e: bot.loop.create_task(after_playing(ctx, e)))

        play_start_time = time.time()

        await ctx.send(f"🎶 Odtwarzam: {os.path.basename(song_path)}")
    else:
        await ctx.send("❌ Plik nie istnieje.")



bot.run(TOKEN)
