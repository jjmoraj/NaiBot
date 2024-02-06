async def cogsList(bot):
    cogs_list = []  # Lista para almacenar nombres de cogs

    for cog_name, cog in bot.cogs.items():
        commands = [f'{command.name}' for command in cog.get_commands()]
        if len(commands) > 0:
            for command in commands:
                # Agregar el nombre del cog a la lista
                cogs_list.append(command)

    return cogs_list
