import re
import os
import json
import discord
from discord.ext import commands
from discord.ui import View, Button, Select
from discord.components import SelectOption
from asyncio import run_coroutine_threadsafe
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
load_dotenv()


class SearchView(View):
    def __init__(self, ctx, song_names, options):
        super().__init__()

        self.ctx = ctx
        self.song_names = song_names
        self.options = options

        self.selected_value = 1

        # Agregar un elemento de selección con las opciones proporcionadas
        self.select_menu = Select(
            options=self.options, custom_id="SelectSearch")
        self.add_item(self.select_menu)

        # Agregar un botón de cancelación
        self.cancel_button = Button(label="Cancelar", custom_id="Cancel",
                                    style=discord.ButtonStyle.danger)
        self.add_item(self.cancel_button)

        self.been_canceled = False

        self.select_menu.callback = self.select_callback
        self.cancel_button.callback = self.button_callback

    async def select_callback(self, interaction: discord.Interaction):
        self.select_menu.disabled = True
        self.cancel_button.disabled = True
        selected_value = self.select_menu.values[0]
        selected_value = int(selected_value)
        selected_song = self.song_names[selected_value]
        await interaction.response.edit_message(view=self)
        await interaction.followup.reply(f"Seleccionaste la opción: {selected_song}")
        self.selected_value = selected_value
        self.stop()

    async def button_callback(self, interaction: discord.Interaction):
        self.select_menu.disabled = True
        self.cancel_button.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.followup.reply("Comando cancelado.")
        self.been_canceled = True
        self.stop()


client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')


class spotify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id, client_secret=client_secret)
        self.sp = Spotify(
            client_credentials_manager=client_credentials_manager)

        self.errorLogo = "https://cdn-icons-png.flaticon.com/512/5387/5387260.png"

        self.is_playing = {}
        self.is_paused = {}
        self.musicQueue = {}
        self.queueIndex = {}

        self.FFMPEG_OPTIONS = {
            # 'ffmpeg': 'ffmpeg',              #! Linux
            'ffmpeg': os.getenv('FFMPEG_EXE'),  # ? Windows
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        self.embedBlue = 0x2c76dd
        self.embedRed = 0xdf1141
        self.embedGreen = 0x00cc03

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
        author = ctx.message.author
        avatar = author.avatar

        songName = song['songName']
        imageURL = song['imageURL']
        artistNames = song['artistNames']
        songURL = song['songURL']
        popularityIndex = song['popularityIndex']

        embed = discord.Embed(
            title=songName,
            url=songURL,
            color=0x00cc03
        )
        embed.set_thumbnail(url=imageURL)
        embed.add_field(name="Nombre de la canción",
                        value=songName, inline=True)
        embed.add_field(name="Artista(s)", value=artistNames, inline=False)
        embed.add_field(name="Índice de popularidad (0-100):",
                        value=popularityIndex, inline=False)
        embed.set_footer(
            text=f'Canción añadida por: {str(author.global_name)}', icon_url=avatar)

        return embed

    def added_song_embed(self, ctx, song):
        author = ctx.message.author
        avatar = author.avatar

        songName = song['songName']
        imageURL = song['imageURL']
        artistNames = song['artistNames']
        songURL = song['songURL']
        popularityIndex = song['popularityIndex']

        embed = discord.Embed(
            title="¡Canción añadida a la lista!",
            url=songURL,
            color=0x00cc03
        )
        embed.set_thumbnail(url=imageURL)
        embed.add_field(name="Nombre de la canción",
                        value=songName, inline=True)
        embed.add_field(name="Artista(s)", value=artistNames, inline=False)
        embed.add_field(name="Índice de popularidad (0-100):",
                        value=popularityIndex, inline=False)
        embed.set_footer(
            text=f'Canción añadida por: {str(author.global_name)}', icon_url=avatar)
        return embed

    def removed_song_embed(self, ctx, song):
        author = ctx.message.author
        avatar = author.avatar

        songName = song['songName']
        imageURL = song['imageURL']
        artistNames = song['artistNames']
        songURL = song['songURL']
        popularityIndex = song['popularityIndex']

        embed = discord.Embed(
            title="¡Canción eliminada a la lista!",
            url=songURL,
            color=0x00cc03
        )
        embed.set_thumbnail(url=imageURL)
        embed.add_field(name="Nombre de la canción",
                        value=songName, inline=True)
        embed.add_field(name="Artista(s)", value=artistNames, inline=False)
        embed.add_field(name="Índice de popularidad (0-100):",
                        value=popularityIndex, inline=False)
        embed.set_footer(
            text=f'Canción eliminada por: {str(author.global_name)}', icon_url=avatar)

        return embed

    def error_embed(self, SEARCH_TERM):
        embed = discord.Embed(color=0x00cc03)
        embed.set_thumbnail(url=self.errorLogo)
        embed.add_field(name="No se han encontrado resultados",
                        value=f"No se han encontrado resultados para '{SEARCH_TERM}', Por favor, inténtalo de nuevo con un valor válido", inline=False)
        return embed

    async def get_song(self, ctx, *args):
        SEARCH_TERM = " ".join(args)
        results = self.sp.search(q=SEARCH_TERM, type='track', limit=5)
        if results['tracks']['items'] == []:
            message = self.error_embed(SEARCH_TERM)
            await ctx.reply(embed=message)
            return
        else:
            song = {}

            song['songName'] = results['tracks']['items'][0]['name']
            song['imageURL'] = results['tracks']['items'][0]['album']['images'][0]['url']
            song['songURL'] = results['tracks']['items'][0]['external_urls']['spotify']
            song['popularityIndex'] = results['tracks']['items'][0]['popularity']

            artistNamesArr = []

            for artists in results['tracks']['items'][0]['artists']:
                artistNamesArr.append(artists['name'])

            song['artistNames'] = ', '.join(map(str, artistNamesArr))

            message = self.now_playing_embed(ctx, song)
            return song

    @commands.command(
        name="artist",
        aliases=["art"],
        description="NAI busca a un artista",
        help="Buscar artistas en spotify",
        brief="Buscar artistas en spotify"
    )
    async def artist(self, ctx, *args):
        SEARCH_TERM = " ".join(args)
        results = self.sp.search(q=SEARCH_TERM, type='artist', limit=5)
        if results['artists']['items'] == []:
            message = self.error_embed(SEARCH_TERM)
            await ctx.reply(embed=message)

        json = results['artists']['items']
        # get artist details
        artistLink = json[0]['external_urls']['spotify']
        artistImage = json[0]['images'][0]['url']
        followers = json[0]['followers']['total']
        genresArr = json[0]['genres']
        if genresArr == []:
            genres = "(No genres specified)"
        else:
            genres = ', '.join(map(str, genresArr))
        popularityIndex = str(json[0]['popularity'])
        artistName = json[0]['name']
        # put details in discord embed
        embed = discord.Embed(title=artistName, url=artistLink, color=0x00cc03)
        embed.set_thumbnail(url=artistImage)
        embed.add_field(name="Número de seguidores:",
                        value=followers, inline=False)
        embed.add_field(name="Géneros:", value=genres, inline=True)
        embed.add_field(name="Índice de popularidad (0-100):",
                        value=popularityIndex, inline=False)
        await ctx.reply(embed=embed)

    @commands.command(
        name="song",
        aliases=["si"],
        description="NAI enseña la información sobre la canción que está sonando",
        help="Información sobre la canción que está sonando",
        brief="Información sobre la canción que está sonando"
    )
    async def song_info(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        spotify_result = next((activity for activity in user.activities if isinstance(
            activity, discord.Spotify)), None)
        if spotify_result is None:
            embed = discord.Embed(title="Ha ocurrido un error", color=0x00cc03)
            embed.set_thumbnail(url=self.errorLogo)
            embed.add_field(
                name=user, value=f"{user.display_name} No esta escuchando nada")
            await ctx.reply(embed=embed)
            return

        embed = discord.Embed(
            title=f"{user.name}'s Spotify",
            description="Escuchando {}".format(spotify_result.title),
            color=0x00cc03)
        embed.set_thumbnail(url=spotify_result.album_cover_url)
        embed.add_field(name="Artista", value=spotify_result.artist)
        embed.add_field(name="Album", value=spotify_result.album)
        embed.set_footer(text="La canción comenzó a las {}".format(
            spotify_result.created_at.strftime("%H:%M")))
        await ctx.reply(embed=embed)

    async def join_VC(self, ctx, channel):
        id = int(ctx.guild.id)
        if self.vc[id] == None or not self.vc[id].is_connected():
            self.vc[id] = await channel.connect()

            if self.vc[id] == None:
                await ctx.reply("No se ha podido conectar al canal de voz")
                return
        else:
            await self.vc[id].move_to(channel)

    def play_next(self, ctx):
        id = int(ctx.guild.id)
        if not self.is_playing[id]:
            return
        if self.queueIndex[id] + 1 < len(self.musicQueue[id]):
            self.is_playing[id] = True
            self.queueIndex[id] += 1

            song = self.musicQueue[id][self.queueIndex[id]][0]
            message = self.now_playing_embed(ctx, song)
            coro = ctx.reply(embed=message)
            fut = run_coroutine_threadsafe(coro, self.bot.loop)
            try:
                fut.result()
            except:
                pass

            self.vc[id].play(discord.FFmpegPCMAudio(
                source=song['songURL'], executable=self.FFMPEG_OPTIONS['ffmpeg']), after=lambda e: self.play_next(ctx))
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
            await ctx.reply(embed=message)

            self.vc[id].play(discord.FFmpegPCMAudio(
                source=song['songURL'], executable=self.FFMPEG_OPTIONS['ffmpeg']), after=lambda e: self.play_next(ctx))
        else:
            await ctx.reply("No hay canciones en la lista.")
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
        id = int(ctx.guild.id)
        try:
            userChannel = ctx.message.author.voice.channel
        except:
            await ctx.reply("NAI no te ve en ningún canal de voz, entra en uno")
            return
        if not args:
            if len(self.musicQueue[id]) == 0:
                await ctx.reply("No hay canciones en la lista")
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
            song = await self.get_song(ctx, *args)
            if type(song) == type(True):
                await ctx.reply("No se ha podido encontrar la canción, pruebe con otra diferente")
            else:
                self.musicQueue[id].append([song, userChannel])

                if not self.is_playing[id]:
                    await self.play_music(ctx)
                else:
                    message = self.added_song_embed(ctx, song)
                    await ctx.reply(embed=message)

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
            await ctx.reply("Debes estar dentro de un canal de voz")
            return
        if not args:
            await ctx.reply("Necesitas especificar una canción para agregar a la lista")
        else:
            song = await self.get_song(ctx, *args)
            if type(song) == type(False):
                await ctx.reply("No se ha podido encontrar la canción, pruebe con otra diferente")
                return
            else:
                self.musicQueue[ctx.guild.id].append([song, userChannel])
                message = self.added_song_embed(ctx, song)
                await ctx.reply(embed=message)

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
            await ctx.reply(embed=removeSongEmbed)
        else:
            await ctx.reply("No hay canciones en la lista")
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
        name="pause",
        aliases=["stop", "pa"],
        description="NAI pausa la canción que está sonando",
        help="Pausar la canción que está sonando",
        brief="Pausar la canción que está sonando"
    )
    async def pause(self, ctx):
        id = int(ctx.guild.id)
        if not self.vc[id]:
            await ctx.reply("No esta sonando nada en este momento.")
        elif self.is_playing[id]:
            await ctx.reply("¡Canción en pausa!")
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
            await ctx.reply("No hay nada para continuar en este momento")
        elif self.is_paused[id]:
            await ctx.reply("¡La canción está sonando!")
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
            await ctx.reply("Necesitas estar dentro de un canal de voz para usar este comando")
        elif self.queueIndex[id] <= 0:
            await ctx.reply("En esta lista no hay canciones anteriores")
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
            await ctx.reply("Necesitas estar dentro de un canal de voz para usar este comando")
        elif self.queueIndex[id] >= len(self.musicQueue[id]) - 1:
            await ctx.reply("No hay canciones siguientes. Volviendo a reproducir la canción")
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
            await ctx.reply("No hay canciones en la lista")
            return

        for i in range(self.queueIndex[id], len(self.musicQueue[id])):
            upNextSongs = len(self.musicQueue[id]) - self.queueIndex[id]
            if i > 5 + upNextSongs:
                break
            returnIndex = i - self.queueIndex[id]
            if returnIndex == 0:
                returnIndex = "Sonando"
            elif returnIndex == 1:
                returnIndex = "Siguiente"
            returnValue += f"{returnIndex} - [{self.musicQueue[id][i]
                                               [0]['title']}]({self.musicQueue[id][i][0]['link']})\n"

            if returnValue == "":
                await ctx.reply("No hay canciones en la lista")
                return

            queue = discord.Embed(
                title="Lista actual",
                description=returnValue,
                colour=self.embedGreen
            )
        await ctx.reply(embed=queue)

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
            await ctx.reply("La lista está vacía")
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
            await ctx.reply(f'NAI se ha unido {userChannel}')
        else:
            await ctx.reply("Necesitas estar conectado a un canal de voz")

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
            await ctx.reply("NAI se fue del chat")
            await self.vc[id].disconnect()
            self.vc[id] = None


""" //- SETUP -// """


async def setup(bot):
    await bot.add_cog(spotify(bot=bot))
