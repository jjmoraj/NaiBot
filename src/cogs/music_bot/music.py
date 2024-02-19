import re
import os
import json
import discord
from discord.ext import commands
import asyncio
from asyncio import run_coroutine_threadsafe
from urllib import parse, request
from youtube_dl import YoutubeDL
from dotenv import load_dotenv
load_dotenv()


class music_bot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.is_playing = {}
        self.is_paused = {}
        self.musicQueue = {}
        self.queueIndex = {}

        self.YTDL_OPTIONS = {
            'format': 'bestaudio/best',
            'nonplaylist': 'True'
        }
        self.FFMPEG_OPTIONS = {
            'ffmpeg': os.getenv('FFMPEG_EXE'),
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        self.embedBlue = 0x2c76dd
        self.embedRed = 0xdf1141
        self.embedGreen = 0x0eaa51

        self.vc = {}

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            id = int(guild.id)
            self.musicQueue[id] = []
            self.queueIndex[id] = 0
            self.vc[id] = None
            self.is_paused[id] = self.is_playing[id] = False

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        id = int(member.guild.id)
        if member.id != self.bot.user.id and before.channel != None and after.channel != before.channel:
            remainingChannelMembers = before.channel.members
            if len(remainingChannelMembers) == 1 and remainingChannelMembers[0].id == self.bot.user.id and self.vc[id].is_connected():
                self.is_playing[id] = self.is_paused[id] = False
                self.musicQueue[id] = []
                self.queueIndex[id] = 0
                await self.vc[id].disconnect()

    def now_playing_embed(self, ctx, song):
        title = song['title']
        link = song['link']
        thumbnail = song['thumbnail']
        author = ctx.message.author
        avatar = author.avatar

        embed = discord.Embed(
            title="Ahora está sonando",
            description=f'[{title}]({link})',
            colour=self.embedBlue,
        )
        embed.set_thumbnail(url=thumbnail)
        embed.set_footer(
            text=f'Canción añadida por: {str(author.global_name)}', icon_url=avatar)
        return embed

    def added_song_embed(self, ctx, song):
        title = song['title']
        link = song['link']
        thumbnail = song['thumbnail']
        author = ctx.message.author
        avatar = author.avatar

        embed = discord.Embed(
            title="¡Canción añadida a la lista!",
            description=f'[{title}]({link})',
            colour=self.embedRed,
        )
        embed.set_thumbnail(url=thumbnail)
        embed.set_footer(
            text=f'Canción añadida por: {str(author.global_name)}', icon_url=avatar)
        return embed

    def removed_song_embed(self, ctx, song):
        title = song['title']
        link = song['link']
        thumbnail = song['thumbnail']
        author = ctx.message.author
        avatar = author.avatar

        embed = discord.Embed(
            title="¡Canción quitada a la lista!",
            description=f'[{title}]({link})',
            colour=self.embedRed,
        )
        embed.set_thumbnail(url=thumbnail)
        embed.set_footer(
            text=f'Canción quitada por: {str(author.global_name)}', icon_url=avatar)
        return embed

    async def join_VC(self, ctx, channel):
        id = int(ctx.guild.id)
        if self.vc[id] == None or not self.vc[id].is_connected():
            self.vc[id] = await channel.connect()

            if self.vc[id] == None:
                await ctx.send("No se ha podido conectar al canal de voz")
                return
        else:
            await self.vc[id].move_to(channel)

    def get_YT_title(self, videoID):
        params = {"format": "json",
                  "url": "https://www.youtube.com/watch?v=%s" % videoID}
        url = "https://www.youtube.com/oembed"
        queryString = parse.urlencode(params)
        url = url + "?" + queryString
        with request.urlopen(url) as response:
            responseText = response.read()
            data = json.loads(responseText.decode())
            return data['title']

    def search_YT(self, search):
        queryString = parse.urlencode({'search_query': search})
        htmContent = request.urlopen(
            'http://www.youtube.com/results?' + queryString)
        searchResults = re.findall(
            '/watch\?v=(.{11})', htmContent.read().decode())
        return searchResults[0:10]

    def extract_YT(self, url):
        with YoutubeDL(self.YTDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
            except:
                return False
        return {
            'link': 'https://www.youtube.com/watch?v=' + url,
            'thumbnail': 'https://i.ytimg.com/vi/' + url + '/hqdefault.jpg?sqp=-oaymwEcCOADEI4CSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLD5uL4xKN-IUfez6KIW_j5y70mlig',
            'source': info['formats'][0]['url'],
            'title': info['title']
        }

    def play_next(self, ctx):
        id = int(ctx.guild.id)
        if not self.is_playing[id]:
            return
        if self.queueIndex[id] + 1 < len(self.musicQueue[id]):
            self.is_playing[id] = True
            self.queueIndex[id] += 1

            song = self.musicQueue[id][self.queueIndex[id]][0]
            message = self.now_playing_embed(ctx, song)
            coro = ctx.send(embed=message)
            fut = run_coroutine_threadsafe(coro, self.bot.loop)
            try:
                fut.result()
            except:
                pass

            self.vc[id].play(discord.FFmpegPCMAudio(
                source=song['source'], executable=self.FFMPEG_OPTIONS['ffmpeg']), after=lambda e: self.play_next(ctx))
        else:
            self.queueIndex[id] += 1
            self.is_playing[id] = False

    async def play_music(self, ctx):
        id = int(ctx.guild.id)
        if self.queueIndex[id] < len(self.musicQueue[id]):
            self.is_playing[id] = True
            self.is_paused[id] = False

            await self.join_VC(ctx, self.musicQueue[id][self.queueIndex[id]][1])

            song = self.musicQueue[id][self.queueIndex[id]][0]
            message = self.now_playing_embed(ctx, song)
            await ctx.send(embed=message)

            self.vc[id].play(discord.FFmpegPCMAudio(
                source=song['source'], executable=self.FFMPEG_OPTIONS['ffmpeg']), after=lambda e: self.play_next(ctx))
        else:
            await ctx.send("No hay canciones en la lista.")
            self.queueIndex[id] += 1
            self.is_playing[id] = False

    @commands.command(
        name="play",
        aliases=["pl"],
        description="NAI pone una canción",
        help="Poner música en el canal de voz",
        brief="Poner música en el canal de voz"
    )
    async def play(self, ctx, *args):
        search = " ".join(args)
        id = int(ctx.guild.id)
        try:
            userChannel = ctx.message.author.voice.channel
        except:
            await ctx.send("NAI no te ve en ningún canal de voz, entra en uno")
            return
        if not args:
            if len(self.musicQueue[id]) == 0:
                await ctx.send("No hay canciones en la lista")
                return
            elif not self.is_playing[id]:
                if self.musicQueue[id] == None or self.vc[id] == None:
                    await self.play_music(ctx)
                else:
                    self.is_paused[id] = False
                    self.is_playing[id] = True
                    self.vc[id].resume()
            else:
                return
        else:
            song = self.extract_YT(self.search_YT(search)[0])
            if type(song) == type(True):
                await ctx.send("No se ha podido encontrar la canción, pruebe con otra diferente")
            else:
                self.musicQueue[id].append([song, userChannel])

                if not self.is_playing[id]:
                    await self.play_music(ctx)
                else:
                    message = self.added_song_embed(ctx, song)
                    await ctx.send(embed=message)

    @commands.command(
        name="add",
        aliases=["a"],
        description="NAI añade resultados a la lista",
        help="Añadir resultados a la lista",
        brief="Añadir resultados a la lista"
    )
    async def add(self, ctx, *args):
        search = " ".join(args)
        try:
            userChannel = ctx.message.author.voice.channel
        except:
            await ctx.send("Debes estar dentro de un canal de voz")
            return
        if not args:
            await ctx.send("Necesitas especificar una canción para agregar a la lista")
        else:
            song = self.extract_YT(self.search_YT(search)[0])
            if type(song) == type(False):
                await ctx.send("No se ha podido encontrar la canción, pruebe con otra diferente")
                return
            else:
                self.musicQueue[ctx.guild.id].append([song, userChannel])
                message = self.added_song_embed(ctx, song)
                await ctx.send(embed=message)

    @commands.command(
        name="remove",
        aliases=["rm"],
        description="NAI quita la ultima canción de la lista",
        help="Eliminar la ultima canción de la cola",
        brief="Eliminar la ultima canción de la cola"
    )
    async def remove(self, ctx):
        id = int(ctx.guild.id)
        if self.musicQueue[id] != []:
            song = self.musicQueue[id][-1][0]
            removeSongEmbed = self.removed_song_embed(ctx, song)
            await ctx.send(embed=removeSongEmbed)
        else:
            await ctx.send("No hay canciones en la lista")
        self.musicQueue[id] = self.musicQueue[id][:-1]
        if self.musicQueue[id] == []:
            if self.vc[id] != None and self.is_playing[id]:
                self.is_playing[id] = self.is_paused[id] = False
                await self.vc[id].disconnect()
                self.vc[id] = None
            self.queueIndex[id] = 0
        elif self.queueIndex[id] == len(self.musicQueue[id]) and self.vc[id] != None and self.vc[id]:
            self.vc[id].pause()
            self.queueIndex[id] -= 1
            await self.play_music(ctx)

    @commands.command(
        name="search",
        aliases=["find", "sr"],
        description="NAI te da una lista de los resultados de la búsqueda",
        help="Devuelve una lista de los resultados de la búsqueda",
        brief="Devuelve una lista de los resultados de la búsqueda"
    )
    async def search(self, ctx, *args):
        search = " ".join(args)
        songNames = []
        selectionOptions = []
        embedText = ""

        if not args:
            await ctx.send("Debe especificar la búsqueda para utilizar este comando")
            return
        try:
            userChannel = ctx.message.author.voice.channel
        except:
            await ctx.send("You must be connected to a voice channel.")
            return

        await ctx.send("Buscando resultados . . .")

        songTokens = self.search_YT(search)

        for i, token in enumerate(songTokens):
            url = 'https://www.youtube.com/watch?v=' + token
            name = self.get_YT_title(token)
            songNames.append(name)
            embedText += f"{i+1} - [{name}]({url})\n"

        for i, title in enumerate(songNames):
            selectionOptions.append(discord.SelectOption(
                self=self, label=f"{i+1} - {title[:95]}", value=i))

        searchResults = discord.Embed(
            title="Search Results",
            description=embedText,
            colour=self.embedRed
        )
        selectionComponents = [
            discord.SelectOption(
                placeholder="Selecciona una opción",
                options=selectionOptions
            ),
            discord.Button(
                label="Cancelar",
                custom_id="Cancel",
                style=4
            )
        ]
        message = await ctx.send(embed=searchResults, components=selectionComponents)
        try:
            tasks = [
                asyncio.create_task(self.bot.wait_for(
                    "button_click",
                    timeout=60.0,
                    check=None
                ), name="button"),
                asyncio.create_task(self.bot.wait_for(
                    "select_option",
                    timeout=60.0,
                    check=None
                ), name="select")
            ]
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            finished = list(done)[0]

            for task in pending:
                try:
                    task.cancel()
                except asyncio.CancelledError:
                    pass

            if finished == None:
                searchResults.title = "Búsqueda Fallida"
                searchResults.description = ""
                await message.delete()
                await ctx.send(embed=searchResults)
                return

            action = finished.get_name()

            if action == "button":
                searchResults.title = "Búsqueda Fallida"
                searchResults.description = ""
                await message.delete()
                await ctx.send(embed=searchResults)
            elif action == "select":
                result = finished.result()
                chosenIndex = int(result.values[0])
                songRef = self.extract_YT(songTokens[chosenIndex])
                if type(songRef) == type(True):
                    await ctx.send("No se pudo descargar la canción. Formato incorrecto, pruebe con otras palabras clave")
                    return
                embedResponse = discord.Embed(
                    title=f"Opción #{chosenIndex + 1} Seleccionada",
                    description=f"¡[{songRef['title']}]({songRef['link']}) Añadida a la lista!",
                    colour=self.embedRed
                )
                embedResponse.set_thumbnail(url=songRef['thumbnail'])
                await message.delete()
                await ctx.send(embed=embedResponse)
                self.musicQueue[ctx.guild.id].append([songRef, userChannel])
        except:
            searchResults.title = "Búsqueda Fallida"
            searchResults.description = ""
            await message.delete()
            await ctx.send(embed=searchResults)

    @commands.command(
        name="pause",
        aliases=["stop", "pa"],
        description="NAI pausa la canción que está sonando",
        help="Pausar la canción que está sonando",
        brief="Pausar la canción que está sonando"
    )
    async def pause(self, ctx):
        id = int(ctx.guild.id)
        if not self.vc[id]:
            await ctx.send("No esta sonando nada en este momento.")
        elif self.is_playing[id]:
            await ctx.send("¡Canción en pausa!")
            self.is_playing[id] = False
            self.is_paused[id] = True
            self.vc[id].pause()

    @commands.command(
        name="resume",
        aliases=["re"],
        description="NAI vuelve a poner la canción que estaba sonando",
        help="Vuelve a poner la canción que está sonando",
        brief="Vuelve a poner la canción que está sonando"
    )
    async def resume(self, ctx):
        id = int(ctx.guild.id)
        if not self.vc[id]:
            await ctx.send("No hay nada para continuar en este momento")
        elif self.is_paused[id]:
            await ctx.send("¡La canción está sonando!")
            self.is_playing[id] = True
            self.is_paused[id] = False
            self.vc[id].resume()

    @commands.command(
        name="previous",
        aliases=["pre", "pr"],
        description="NAI pone la ultima canción de la lista",
        help="Vuelve a poner la canción que acaba de sonar",
        brief="Vuelve a poner la canción que acaba de sonar"
    )
    async def previous(self, ctx):
        id = int(ctx.guild.id)
        if self.vc[id] == None:
            await ctx.send("Necesitas estar dentro de un canal de voz para usar este comando")
        elif self.queueIndex[id] <= 0:
            await ctx.send("En esta lista no hay canciones anteriores")
            self.vc[id].pause()
            await self.play_music(ctx)
        elif self.vc[id] != None and self.vc[id]:
            self.vc[id].pause()
            self.queueIndex[id] -= 1
            await self.play_music(ctx)

    @commands.command(
        name="skip",
        aliases=["sk"],
        description="NAI pone la siguiente canción de la lista",
        help="Pones la siguiente canción de la lista",
        brief="Pones la siguiente canción de la lista"
    )
    async def skip(self, ctx):
        id = int(ctx.guild.id)
        if self.vc[id] == None:
            await ctx.send("Necesitas estar dentro de un canal de voz para usar este comando")
        elif self.queueIndex[id] >= len(self.musicQueue[id]) - 1:
            await ctx.send("No hay canciones siguientes. Volviendo a reproducir la canción")
            self.vc[id].pause()
            await self.play_music(ctx)
        elif self.vc[id] != None and self.vc[id]:
            self.vc[id].pause()
            self.queueIndex[id] += 1
            await self.play_music(ctx)

    @commands.command(
        name="queue",
        aliases=["list", "q"],
        description="NAI devuelve la lista de canciones",
        help="Ver la lista de canciones",
        brief="Ver la lista de canciones"
    )
    async def queue(self, ctx):
        id = int(ctx.guild.id)
        returnValue = ""
        if self.musicQueue[id] == []:
            await ctx.send("No hay canciones en la lista")
            return

        for i in range(self.queueIndex[id], len(self.musicQueue[id])):
            upNextSongs = len(self.musicQueue[id]) - self.queueIndex[id]
            if i > 5 + upNextSongs:
                break
            returnIndex = i - self.queueIndex[id]
            if returnIndex == 0:
                returnIndex = "Playing"
            elif returnIndex == 1:
                returnIndex = "Next"
            returnValue += f"{returnIndex} - [{self.musicQueue[id][i][0]['title']}]({self.musicQueue[id][i][0]['link']})\n"

            if returnValue == "":
                await ctx.send("No hay canciones en la lista")
                return

        queue = discord.Embed(
            title="Current Queue",
            description=returnValue,
            colour=self.embedGreen
        )
        await ctx.send(embed=queue)

    @commands.command(
        name="clear",
        aliases=["cl"],
        description="NAI limpia la lista de canciones",
        help="Limpiar la lista de canciones",
        brief="Limpiar la lista de canciones"
    )
    async def clear(self, ctx):
        id = int(ctx.guild.id)
        if self.vc[id] != None and self.is_playing[id]:
            self.is_playing = self.is_paused = False
            self.vc[id].stop()
        if self.musicQueue[id] != []:
            await ctx.send("La lista está vacía")
            self.musicQueue[id] = []
        self.queueIndex = 0

    @commands.command(
        name="join",
        aliases=["j"],
        description="NAI se conecta al canal de voz",
        help="Conectas al bot al canal de voz",
        brief="Conectas al bot al canal de voz"
    )
    async def join(self, ctx):
        #! Para ver los atributos del objeto avatar:
        # print(dir(ctx.message.author))

        if ctx.message.author.voice:
            userChannel = ctx.message.author.voice.channel
            await self.join_VC(ctx, userChannel)
            await ctx.send(f'NAI se ha unido {userChannel}')
        else:
            await ctx.send("Necesitas estar conectado a un canal de voz")

    @commands.command(
        name="leave",
        aliases=["l"],
        description="NAI se va del canal de voz",
        help="Echas al bot del canal de voz",
        brief="Echas al bot del canal de voz"
    )
    async def leave(self, ctx):
        id = int(ctx.guild.id)
        self.is_playing[id] = self.is_paused[id] = False
        self.musicQueue[id] = []
        self.queueIndex[id] = 0
        if self.vc[id] != None:
            await ctx.send("NAI se fue del chat")
            await self.vc[id].disconnect()
            self.vc[id] = None


""" //- SETUP -// """


async def setup(bot):
    await bot.add_cog(music_bot(bot=bot))
