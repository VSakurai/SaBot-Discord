import platform
import random
import psutil
import time
import aiohttp
import datetime
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

from helpers import checks, db_manager
from Settings.config import EMBED_COLOR

class CogDeveloper(commands.Cog, name="developer"):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.datetime.utcnow()

    @commands.hybrid_command(
        name="shutdown",
        description="Сделайте так, чтобы бот выключился.",
    )
    @checks.is_owner()
    async def shutdown(self, context: Context) -> None:
        """
        Выключает бота.

         :param context: Контекст гибридной команды.
        """
        embed = discord.Embed(
            description="Выключение. Пока! :wave:",
            color=EMBED_COLOR
        )
        await context.send(embed=embed)
        await self.bot.close()

    @commands.hybrid_command(
        name="say",
        description="Бот скажет все, что вы хотите.",
    )
    @app_commands.describe(message="Сообщение, которое должен повторить бот")
    @checks.is_owner()
    async def say(self, context: Context, *, message: str) -> None:
        """
        Бот скажет все, что вы хотите.

         :param context: Контекст гибридной команды.
         :param message: Сообщение, которое должен повторить бот.
        """
        await context.send(message)

    @commands.hybrid_command(
        name="embed",
        description="Бот скажет все, что вы хотите, но внутри встраивания.",
    )
    @app_commands.describe(message="Сообщение, которое должен повторить бот")
    @checks.is_owner()
    async def embed(self, context: Context, *, message: str) -> None:
        """
        Бот будет говорить все, что вы хотите, но с помощью встраивания.

         :param context: Контекст гибридной команды.
         :param message: Сообщение, которое должен повторить бот.
        """
        embed = discord.Embed(
            description=message,
            color=EMBED_COLOR
        )
        await context.send(embed=embed)

    @commands.hybrid_group(
        name="blacklist",
        description="Получить список всех пользователей из черного списка.",
    )
    @checks.is_owner()
    async def blacklist(self, context: Context) -> None:
        """
        Lets you add or remove a user from not being able to use the bot.

        :param context: The hybrid command context.
        """
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                description="Вам нужно указать подкоманду.\n\n**Подкоманды:**\n`add` - Добавить пользователя в ЧС.\n`remove` - Удалить пользователя из ЧС.\n`show` - Посмотреть список пользователей в ЧС.",
                color=EMBED_COLOR
            )
            await context.send(embed=embed)

    @blacklist.command(
        base="blacklist",
        name="show",
        description="Показывает список всех пользователей из черного списка.",
    )
    @checks.is_owner()
    async def blacklist_show(self, context: Context) -> None:
        """
        Shows the list of all blacklisted users.

        :param context: The hybrid command context.
        """
        blacklisted_users = await db_manager.get_blacklisted_users()
        if len(blacklisted_users) == 0:
            embed = discord.Embed(
                description="В настоящее время нет пользователей в черном списке.",
                color=EMBED_COLOR
            )
            await context.send(embed=embed)
            return

        embed = discord.Embed(
            title="Пользователи из черного списка",
            color=EMBED_COLOR
        )
        users = []
        for bluser in blacklisted_users:
            user = self.bot.get_user(int(bluser[0])) or await self.bot.fetch_user(int(bluser[0]))
            users.append(
                f"• {user.mention} ({user}) - В черный списке с <t:{bluser[1]}>")
        embed.description = "\n".join(users)
        await context.send(embed=embed)

    @blacklist.command(
        base="blacklist",
        name="add",
        description="Позволяет добавить пользователя в ЧС бота.",
    )
    @app_commands.describe(user="Пользователь, который должен быть добавлен в черный список")
    @checks.is_owner()
    async def blacklist_add(self, context: Context, user: discord.User) -> None:
        """
        Lets you add a user from not being able to use the bot.

        :param context: The hybrid command context.
        :param user: The user that should be added to the blacklist.
        """
        user_id = user.id
        if await db_manager.is_blacklisted(user_id):
            embed = discord.Embed(
                description=f"**{user.name}** уже в черном списке.",
                color=EMBED_COLOR
            )
            await context.send(embed=embed)
            return
        total = await db_manager.add_user_to_blacklist(user_id)
        embed = discord.Embed(
            description=f"**{user.name}** был успешно добавлен в черный список",
            color=EMBED_COLOR
        )
        embed.set_footer(
            text=f"Там {'является' if total == 1 else 'являются'} теперь {total} {'пользователь' if total == 1 else 'пользователи'} в черном списке"
        )
        await context.send(embed=embed)

    @blacklist.command(
        base="blacklist",
        name="remove",
        description="Позволяет убрать пользователя из ЧС бота.",
    )
    @app_commands.describe(user="Пользователь, которого следует удалить из черного списка.")
    @checks.is_owner()
    async def blacklist_remove(self, context: Context, user: discord.User) -> None:
        """
        Lets you remove a user from not being able to use the bot.

        :param context: The hybrid command context.
        :param user: The user that should be removed from the blacklist.
        """
        user_id = user.id
        if not await db_manager.is_blacklisted(user_id):
            embed = discord.Embed(
                description=f"**{user.name}** нет в черном списке.",
                color=EMBED_COLOR
            )
            await context.send(embed=embed)
            return
        total = await db_manager.remove_user_from_blacklist(user_id)
        embed = discord.Embed(
            description=f"**{user.name}** был успешно удален из черного списка",
            color=EMBED_COLOR
        )
        embed.set_footer(
            text=f"Там {'является' if total == 1 else 'являются'} теперь {total} {'пользователь' if total == 1 else 'пользователи'} в черном списке"
        )
        await context.send(embed=embed)

    @commands.command(
        name="sync",
        description="Синхронизирует слэш-команды.",
    )
    @app_commands.describe(scope="Объем синхронизации. Может быть `global` или `guild`.")
    @checks.is_owner()
    async def sync(self, context: Context, scope: str) -> None:
        """
        Синхронизирует слэш-команды.

         :param context: Контекст команды.
         :param scope: Область синхронизации. Может быть «глобальным» или «гильдийным».
        """

        if scope == "global":
            await context.bot.tree.sync()
            embed = discord.Embed(
                description="Слеш-команды глобально синхронизированы.",
                color=EMBED_COLOR
            )
            await context.send(embed=embed)
            return
        elif scope == "guild":
            context.bot.tree.copy_global_to(guild=context.guild)
            await context.bot.tree.sync(guild=context.guild)
            embed = discord.Embed(
                description="Слэш-команды синхронизированы в этой гильдии.",
                color=EMBED_COLOR
            )
            await context.send(embed=embed)
            return
        embed = discord.Embed(
            description="Область применения должна быть `global` или `guild`.",
            color=EMBED_COLOR
        )
        await context.send(embed=embed)

    @commands.command(
        name="unsync",
        description="Отменяет синхронизацию слэш-команд.",
    )
    @app_commands.describe(scope="Объем синхронизации. Возможно `global`, `current_guild` или `guild`")
    @checks.is_owner()
    async def unsync(self, context: Context, scope: str) -> None:
        """
        Отменяет синхронизацию слэш-команд.

         :param context: Контекст команды.
         :param scope: Область синхронизации. Может быть «глобальным», «current_guild» или «guild».
        """

        if scope == "global":
            context.bot.tree.clear_commands(guild=None)
            await context.bot.tree.sync()
            embed = discord.Embed(
                description="Слеш-команды глобально не синхронизированы.",
                color=EMBED_COLOR
            )
            await context.send(embed=embed)
            return
        elif scope == "guild":
            context.bot.tree.clear_commands(guild=context.guild)
            await context.bot.tree.sync(guild=context.guild)
            embed = discord.Embed(
                description="Слеш-команды в этой гильдии не синхронизированы.",
                color=EMBED_COLOR
            )
            await context.send(embed=embed)
            return
        embed = discord.Embed(
            description="Область применения должна быть `global` или `guild`.",
            color=EMBED_COLOR
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="load",
        description="Загрузить модуль",
    )
    @app_commands.describe(cog="Имя модуля для загрузки")
    @checks.is_owner()
    async def load(self, context: Context, cog: str) -> None:
        """
        The bot will load the given cog.

        :param context: The hybrid command context.
        :param cog: The name of the cog to load.
        """
        try:
            await self.bot.load_extension(f"Cogs.{cog}")
        except Exception:
            embed = discord.Embed(
                description=f"Не удалось загрузить модуль `{cog}`.",
                color=EMBED_COLOR
            )
            await context.send(embed=embed)
            return
        embed = discord.Embed(
            description=f"Успешно загружен модуль `{cog}`.",
            color=EMBED_COLOR
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="unload",
        description="Выгружает модуль.",
    )
    @app_commands.describe(cog="Имя модуль для выгрузки")
    @checks.is_owner()
    async def unload(self, context: Context, cog: str) -> None:
        """
        The bot will unload the given cog.

        :param context: The hybrid command context.
        :param cog: The name of the cog to unload.
        """
        try:
            await self.bot.unload_extension(f"Cogs.{cog}")
        except Exception:
            embed = discord.Embed(
                description=f"Не удалось выгрузить модуль `{cog}`.",
                color=EMBED_COLOR
            )
            await context.send(embed=embed)
            return
        embed = discord.Embed(
            description=f"Успешно выгружена модуль `{cog}`.",
            color=EMBED_COLOR
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="reload",
        description="Перезагружает модули.",
    )
    @app_commands.describe(cog="Имя модуля для перезагрузки")
    @checks.is_owner()
    async def reload(self, context: Context, cog: str) -> None:
        try:
            await self.bot.reload_extension(f"Cogs.{cog}")
        except Exception:
            embed = discord.Embed(
                description=f"Не удалось перезагрузить модуль `{cog}`.",
                color=EMBED_COLOR
            )
            await context.send(embed=embed)
            return
        embed = discord.Embed(
            description=f"Успешно перезагружена модуль `{cog}`.",
            color=EMBED_COLOR
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="botinfo",
        description="Информация о боте"
    )
    @checks.is_owner()
    async def botinfo(self, ctx):
        total_members = sum(guild.member_count for guild in self.bot.guilds)
        total_channels = sum(1 for _ in self.bot.get_all_channels())
        total_voice = sum(1 for guild in self.bot.guilds for channel in guild.voice_channels)

        # Получаем текущее время UTC
        now_utc = datetime.datetime.utcnow()

        # Вычисляем время работы бота
        uptime = now_utc - self.start_time
        duration = format_time_delta(uptime)

        # Отправляем информацию о боте
        await ctx.send(
            embed=discord.Embed(
                title="ℹ️ **Информация о боте**",
                description="",
                color=EMBED_COLOR
            ).add_field(
                name="⚙️ Основное",
                value=f"\n"
                      f"🤖 Имя бота: **{self.bot.user.name}**\n"
                      f"🆔 ID бота: **{self.bot.user.id}**\n"
                      f"🔧 Владелец бота: <@!401125141788229632>\n"
                      f"👥 Пользователей: **{total_members}** шт.\n"
                      f"🔊 Голосовых каналов: **{total_voice}** шт.\n"
                      f"📺 Каналов: **{total_channels}** шт.\n"
                      f"📅 Создан: **{self.bot.user.created_at.strftime('%Y-%m-%d %H:%M:%S')}** UTC\n"
                      f"\n",
                inline=False
            ).add_field(
                name="⏱️ Система",
                value=f"\n"
                      f"🆙 Время работы: **{duration}**\n"
                      f"⌛ Скорость API: **{round(self.bot.latency * 1000)}** мс\n"
                      f"🏷️ Версия Python: **{platform.python_version()}**\n"
                      f"💾 Память бота: **{get_process_memory_usage():.2f}** MB",
                inline=False
            )
        )

def format_time_delta(delta):
    seconds = delta.total_seconds()
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{int(days)} дней, {int(hours)} часов, {int(minutes)} минут, {int(seconds)} секунд"

def get_process_memory_usage():
    process = psutil.Process()
    return process.memory_info().rss / (1024 * 1024)  # Возвращаем память в MB


async def setup(bot):
    await bot.add_cog(CogDeveloper(bot))
