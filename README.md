# NaiBot

# Commands / Cogs / Events

# discord.py: Comandos, Cogs y Eventos

## Comandos

Un comando en discord.py es una función que se invoca mediante un mensaje de texto en Discord. Cada comando se marca con el decorador `commands.command()`. Los comandos son la forma principal de interactuar con un bot de Discord.

```python
@commands.command()
async def hola(self, ctx):
    await ctx.send('¡Hola!')
```

## Cogs

Un cog en discord.py es una clase de Python que hereda de `commands.Cog`. Los cogs son una forma de organizar tus comandos y listeners (oyentes) en una sola clase. Esto es útil para mantener tu código ordenado y modular.

```python
class Saludos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hola(self, ctx):
        await ctx.send('¡Hola!')
```

Para registrar un cog, usamos el método `add_cog()`:

```python
bot.add_cog(Saludos(bot))
```

Para eliminar un cog, usamos el método `remove_cog()`:

```python
bot.remove_cog('Saludos')
```

## Eventos (Listeners)

Los eventos, también conocidos como listeners, son funciones que el bot ejecuta en respuesta a ciertos eventos en Discord. Por ejemplo, puedes tener un evento que se dispara cuando un usuario se une a un servidor, cuando un mensaje se envía, etc. Los eventos se marcan con el decorador `commands.Cog.listener()`.

```python
@commands.Cog.listener()
async def on_member_join(self, member):
    await member.guild.system_channel.send(f'¡Bienvenido {member.mention}!')
```
