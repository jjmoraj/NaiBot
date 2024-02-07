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

# Propiedades de los comandos

En la biblioteca discord.py, los comandos tienen varias propiedades y métodos que puedes utilizar para obtener información y realizar diversas acciones. Algunas de las propiedades más comunes de los comandos incluyen:

1. **`name`**: El nombre del comando.

2. **`aliases`**: Una lista de alias (otros nombres) que pueden usarse para invocar el comando.

3. **`brief`**: Una breve descripción del comando, utilizada para proporcionar información concisa sobre el comando.

4. **`help`**: La ayuda detallada del comando, que proporciona información más extensa sobre su uso.

5. **`usage`**: Una cadena que representa cómo se debe usar el comando, incluyendo los argumentos.

6. **`enabled`**: Indica si el comando está habilitado o deshabilitado.

7. **`hidden`**: Indica si el comando debe estar oculto en la ayuda.

8. **`cog`**: La instancia del cog al que pertenece el comando.

9. **`cooldown`**: La configuración de cooldown para el comando.

10. **`parent`**: En el caso de subcomandos, representa el comando principal al que están subordinados.

Estas son solo algunas de las propiedades más comunes. Puedes explorar la documentación oficial de discord.py para obtener información detallada sobre las propiedades y métodos de los comandos: [discord.py - Comandos](https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Command)
# NaiBot
# NaiBot
