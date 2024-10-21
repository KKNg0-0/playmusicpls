import discord
import os
import asyncio
import yt_dlp
from dotenv import load_dotenv

# Code Tutorial by Ethan | The Code Syndicate
current_song = 0

def run_bot():
    load_dotenv()
    TOKEN = os.getenv('discord_token')
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    
    voice_clients = {}
    yt_dl_options = {"format": "bestaudio/best"}
    ytdl = yt_dlp.YoutubeDL(yt_dl_options)
    
    ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.25"'}
    
    playlists = []          # playlist to manage
    
    def playlist_store(url, title):
        playlists.append({
            'url': url,
            'title': title,
        })
        pass
    
    async def play_next(voice_client):
        global current_song
        if current_song < len(playlists):
            song_data = playlists[current_song]
            source = discord.FFmpegPCMAudio(song_data['url'], **ffmpeg_options)
            
            voice_client.play(source, after=lambda e: client.loop.create_task(play_next(voice_client)))
            current_song += 1
        else:
            await voice_client.disconnect()
            current_song = 0
        
    @client.event
    async def on_ready():
        print(f'{client.user} is now jamming')
        
    @client.event
    async def on_message(message):
        if message.content.startswith("!play"):
            try:
                voice_client = await message.author.voice.channel.connect() # join the voice channel of the author of the command
                voice_clients[voice_client.guild.id] = voice_client
            except Exception as e:
                print(e)
            
            try:
                url = message.content.split()[1]
                
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
                
                playlist_store(data['url'], data['title'])
                
                if len(playlists) > 0:
                    song = playlists[current_song]['url']
                    player = discord.FFmpegPCMAudio(song, **ffmpeg_options)
                    
                    voice_clients[message.guild.id].play(player, after=lambda e: client.loop.create_task(play_next(voice_clients[message.guild.id])))
                
                #song = data['url']
                #player = discord.FFmpegPCMAudio(song, **ffmpeg_options) # play the song using the ffmpeg options
                
                v#oice_clients[message.guild.id].play(player)
            except Exception as e:
                print(e)
                
        if message.content.startswith("!pause"):
            try:
                voice_clients[message.guild.id].pause()
            except Exception as e:
                print(e)
                
        if message.content.startswith("!resume"):
            try:
                voice_clients[message.guild.id].resume()
            except Exception as e:
                print(e)  
                      
        if message.content.startswith("!stop"):
            try:
                voice_clients[message.guild.id].stop()
                await voice_clients[message.guild.id].disconnect()
            except Exception as e:
                print(e)

        if message.content.startswith("!skip"):
            pass
        
        if message.content.startswith("!now"):
            pass
    
    client.run(TOKEN)
    
                