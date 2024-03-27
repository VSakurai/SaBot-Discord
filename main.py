import asyncio
import os
import platform
import random
import sys
import aiosqlite
import discord
import exceptions
from discord.ext import commands, tasks
from discord.ext.commands import Bot, Context
from discord.enums import ActivityType
from keep_alive import keep_alive

from Settings.config import (BOT_TOKEN, BOT_PREFIX, BOT_SYNC_COMMANDS_GlOBALLY,
                             BOT_AUTO_ROLE_ID, BOT_NOTICE_CHANNEL, BOT_USE_EDIT_NOTICE,
                             BOT_USE_REMOVE_NOTICE, LIST_OF_FORBIDDEN_CHANNELS)

#keep_alive()

intents = discord.Intents.default()
intents.members = True
intents.typing = True
intents.presences = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents, help_command=None)

async def init_db():
    async with aiosqlite.connect(f"{os.path.realpath(os.path.dirname(__file__))}/DataBase/database.db") as db:
        with open(f"{os.path.realpath(os.path.dirname(__file__))}/DataBase/schema.sql") as file:
            await db.executescript(file.read())
        await db.commit()

@bot.event
async def on_ready() -> None:
    print("------------------------------")
    print(f"Вы вошли как {bot.user.name}")
    print(f"Версия API discord.py: {discord.__version__}")
    print(f"Версия Python: {platform.python_version()}")
    print(f"Работает на: {platform.system()} {platform.release()} ({os.name})")
    print(f"Скорость API: {round(bot.latency * 1000)} мс")
    print("------------------------------")
    status_task.start()
    if BOT_SYNC_COMMANDS_GlOBALLY:
        print("Глобальная синхронизация команд...")
        await bot.tree.sync()

@tasks.loop(minutes=10.0)
async def status_task():
    statuses = ["RADMIR CRMP", "На вписке", "потерялся", "На чиле", "Хочу банан", "Слушаю порнуху", "Музыкант"]
    activity_type = random.choice([ActivityType.playing, ActivityType.streaming, ActivityType.listening, ActivityType.watching])
    activity_text = random.choice(statuses)
    await bot.change_presence(activity=discord.Activity(type=activity_type, name=activity_text))

@bot.event
async def on_member_join(member):
    guild = bot.get_guild(BOT_SERVER)
    if guild:  # Проверка на нужный сервер
        role = guild.get_role(BOT_AUTO_ROLE_ID)
        if role:
            await member.add_roles(role)
            print(f'Пользователь {member.name} ({member.id}) присоединился к серверу в {member.joined_at} и получил роль {role.name}.')
            if BOT_USE_NEWCOMER_NOTICE:
                await send_notice(f'Пользователь **{member.mention}** присоединился к серверу и получил роль {role.name}.')

@bot.event
async def on_member_remove(member):
    guild = bot.get_guild(BOT_SERVER)
    if guild:  # Проверка на нужный сервер
        print(f'Пользователь {member.name} ({member.id}) покинул сервер в {discord.utils.utcnow()}.')
        if BOT_USE_REMOVE_NOTICE:
            await send_notice(f'Пользователь {member.name} покинул сервер.')

@bot.event
async def on_message_edit(before, after):
    if BOT_USE_EDIT_NOTICE and before.guild:
        if before.channel.id not in LIST_OF_FORBIDDEN_CHANNELS:  # Здесь LIST_OF_FORBIDDEN_CHANNELS - список ID каналов, из которых не нужно отправлять логи
            print(f'Сообщение "{before.content}" было изменено на "{after.content}" пользователем {before.author} в канале {before.channel}.')
            await send_notice(f'Сообщение `{before.content}` было изменено на `{after.content}` пользователем **{before.author}** в канале **{before.channel}**.')

@bot.event
async def on_message_delete(message):
    if BOT_USE_REMOVE_NOTICE and message.guild:
        if message.channel.id not in LIST_OF_FORBIDDEN_CHANNELS:  # Здесь LIST_OF_FORBIDDEN_CHANNELS - список ID каналов, из которых не нужно отправлять логи
            print(f'Сообщение "{message.content}" было удалено пользователем {message.author} в канале {message.channel}.')
            await send_notice(f'Сообщение `{message.content}` было удалено пользователем **{message.author}** в канале **{message.channel}**.')

async def send_notice(message):
    channel = bot.get_channel(BOT_NOTICE_CHANNEL)
    if channel:
        await channel.send(message)

@bot.event
async def on_message(message: discord.Message) -> None:
    """
    Код в этом событии выполняется каждый раз, когда кто-то отправляет сообщение, с префиксом или без него.
    :param message: Сообщение, которое было отправлено.
    """
    if message.author == bot.user or message.author.bot:
        return
    await bot.process_commands(message)

@bot.event
async def on_command_completion(context: Context) -> None:
    """
    Код в этом событии выполняется каждый раз, когда обычная команда была *успешно* выполнена.
    :param context: контекст выполненной команды.
    """
    full_command_name = context.command.qualified_name
    split = full_command_name.split(" ")
    executed_command = str(split[0])
    if context.guild is not None:
        print(
            f"Выполненная /{executed_command} команда в {context.guild.name} (ID: {context.guild.id}) от {context.author} (ID: {context.author.id})")
    else:
        print(
            f"Выполненная /{executed_command} команда от {context.authorauthor} (ID: {context.author.id}) в ЛС")

@bot.event
async def on_command_error(context: Context, error) -> None:
    """
    Код в этом событии выполняется каждый раз, когда обычная допустимая команда обнаруживает ошибку.

     :param context: Контекст обычной команды, которая не выполнилась.
     :param error: Возникшая ошибка.
    """
    if isinstance(error, commands.CommandOnCooldown):
        minutes, seconds = divmod(error.retry_after, 60)
        hours, minutes = divmod(minutes, 60)
        hours = hours % 24
        embed = discord.Embed(
            description=f"**Пожалуйста, помедленнее** - Вы можете снова использовать эту команду в {f'{round(hours)} час(ов)' if round(hours) > 0 else ''} {f'{round(minutes)} мин.' if round(minutes) > 0 else ''} {f'{round(seconds)} сек.' if round(seconds) > 0 else ''}.",
            color=0xE02B2B
        )
        await context.send(embed=embed)
    elif isinstance(error, exceptions.UserBlacklisted):
        """
        Код здесь будет выполняться только в том случае, если ошибка является экземпляром «UserBlacklisted», что может произойти при использовании
         проверьте @checks.not_blacklisted() в своей команде, или вы можете вызвать ошибку самостоятельно.
        """
        embed = discord.Embed(
            description="Вы внесены в черный список от использования бота!",
            color=0xE02B2B
        )
        await context.send(embed=embed)
        print(
            f"{context.author} (ID: {context.author.id}) пытался выполнить команду в гильдии {context.guild.name} (ID: {context.guild.id}), но пользователь занесен в черный список от использования бота.")
    elif isinstance(error, exceptions.UserNotOwner):
        """
        То же, что и выше, только для проверки @checks.is_owner().
        """
        embed = discord.Embed(
            description="Вы не являетесь владельцем бота!",
            color=0xE02B2B
        )
        await context.send(embed=embed)
        print(
            f"{context.author} (ID: {context.author.id}) пытался выполнить команду только владельца в гильдии {context.guild.name} (ID: {context.guild.id}), но пользователь не является владельцем бота.")
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            description="Вам не хватает разрешений `" + ", ".join(
                error.missing_permissions) + "` выполнить эту команду!",
            color=0xE02B2B
        )
        await context.send(embed=embed)
    elif isinstance(error, commands.BotMissingPermissions):
        embed = discord.Embed(
            description="Мне не хватает разрешений `" + ", ".join(
                error.missing_permissions) + "` чтобы полностью выполнить эту команду!",
            color=0xE02B2B
        )
        await context.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="Ошибка!",
            # Нам нужно использовать заглавные буквы, потому что аргументы команды не имеют заглавной буквы в коде.
            description=str(error).capitalize(),
            color=0xE02B2B
        )
        await context.send(embed=embed)
    else:
        raise error

async def load_cogs() -> None:
    """
    Код в этой функции выполняется при каждом запуске бота.
    """
    for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/Cogs"):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                await bot.load_extension(f"Cogs.{extension}")
                print(f"Загруженное расширение '{extension}'")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                print(f"Не удалось загрузить расширение {extension}\n{exception}")


asyncio.run(init_db())
asyncio.run(load_cogs())
bot.run(BOT_TOKEN, reconnect=True)