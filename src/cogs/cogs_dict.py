async def get_cogs_dict(bot):
    cogs_dict = {}  # Lista para almacenar nombres de cogs

    for cog_name, cog in bot.cogs.items():
        commands_names = [f'{command.name}' for command in cog.get_commands()]
        commands_descriptions = [
            f'{command.description}' for command in cog.get_commands()]
        for i in range(0, len(commands_names)):
            command_name = commands_names[i]
            command_description = commands_descriptions[i]
            cogs_dict[command_name] = command_description
    return cogs_dict
