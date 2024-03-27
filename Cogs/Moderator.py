import discord
import asyncio
import datetime
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

from Settings import config

from helpers import checks, db_manager

class CogModerator(commands.Cog, name="Moderator"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="announce",
        description="Отправить объявление в указанный канал."
    )
    @commands.has_guild_permissions(manage_messages=True)
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    @checks.not_blacklisted()
    async def announce(self, ctx, channel: discord.TextChannel, *, message):
        await channel.send(embed=discord.Embed(
            title="📢・Объявление!",
            description=message
        ))

        await ctx.send(embed=discord.Embed(
            title="✅ Объявление отправлено!",
            description=f"Объявление успешно отправлено на адрес {channel.mention}."
        ))

    @commands.hybrid_command(
        name="unmute",
        description="Снять текстовый мут с игрока",
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    @checks.not_blacklisted()
    @app_commands.describe(
        user="Пользователь, которого следует снять текстовый мут.",  
        reason="Причина, по которой пользователю снимется текстовый мут.")
    async def unmute(self, ctx: commands.Context, user: discord.Member, *, reason: str = "Без причины") -> None:
        mute_role = discord.utils.get(ctx.guild.roles, name="Text Mute")
        if not mute_role:
            embed = discord.Embed(
                title="Ошибка",
                description="Роль для снятие мута не найдена. Создайте роль `Text Mute`.",
                color=config.EMBED_COLOR
            )
            await ctx.send(embed=embed)
            return
        if user == ctx.author:
            embed = discord.Embed(
                description="Вы не можете снять мут самому себе",
                color=config.EMBED_COLOR
            )
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            description=f"**{ctx.author}**, снял с игрока **{user.mention}** текстовый мут по причине: `{reason}`",
            color=config.EMBED_COLOR
        )
        await user.remove_roles(mute_role)
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="un_vmute",
        description="Снять голосовой мут с игрока",
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    @checks.not_blacklisted()
    @app_commands.describe(
        user="Пользователь, которого следует снять голосовой мут.",  
        reason="Причина, по которой пользователю снимется голосовой мут.")
    async def un_vmute(self, ctx: commands.Context, user: discord.Member, *, reason: str = "Без причины") -> None:
        mute_role = discord.utils.get(ctx.guild.roles, name="Voice Mute")
        if not mute_role:
            embed = discord.Embed(
                title="Ошибка",
                description="Роль для снятие мута не найдена. Создайте роль `Voice Mute`.",
                color=config.EMBED_COLOR
            )
            await ctx.send(embed=embed)
            return
        if user == ctx.author:
            embed = discord.Embed(
                description="Вы не можете снять мут самому себе",
                color=config.EMBED_COLOR
            )
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            description=f"**{ctx.author}**, снял с игрока **{user.mention}** голосовой мут по причине: `{reason}`",
            color=config.EMBED_COLOR
        )
        await user.remove_roles(mute_role)
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="vmute",
        description="Выдать голосовой мут на время",
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    @checks.not_blacklisted()
    @app_commands.describe(
        user="Пользователь, которого следует выдать мут.", 
        time="Время на которое выдать мут пользователя `s`, `m`, `h`, `d`", 
        reason="Причина, по которой пользователь должен быть замучен.")
    async def vmute(self, ctx: commands.Context, user: discord.Member, time: str = None, *, reason: str = "Без причины") -> None:
        mute_role = discord.utils.get(ctx.guild.roles, name="Voice Mute")
        if not mute_role:
            embed = discord.Embed(
                title="Ошибка",
                description="Роль для снятие мута не найдена. Создайте роль `Voice Mute`.",
                color=config.EMBED_COLOR
            )
            await ctx.send(embed=embed)
            return
        if user == ctx.author:
            embed = discord.Embed(
                description="Вы не можете выдать мут самому себе",
                color=config.EMBED_COLOR
            )
            await ctx.send(embed=embed)
            return
        if user.top_role.position >= ctx.author.top_role.position:
            embed = discord.Embed(
                description="Вы не можете выдать мут пользователю с ролью выше вашей.",
                color=config.EMBED_COLOR
            )
            await ctx.send(embed=embed)
            return
        if mute_role in user.roles:
            embed = discord.Embed(
                description=f"{user.mention} уже замучен.",
                color=config.EMBED_COLOR
            )
            await ctx.send(embed=embed)
            return
        if time:
            if len(time) < 2 or time[-1] not in "smhd":
                embed = discord.Embed(
                    title="Ошибка",
                    description="Некорректное время для мута.",
                    color=config.EMBED_COLOR
                )
                await ctx.send(embed=embed)
                return
            amount = int(time[:-1])
            if amount <= 0:
                embed = discord.Embed(
                    title="Ошибка",
                    description="Время не может быть меньше 1!",
                    color=config.EMBED_COLOR
                )
                await ctx.send(embed=embed)
                return
            if time.endswith("s"):
                time_in_seconds = amount
                time_unit = "секунд"
            elif time.endswith("m"):
                time_in_seconds = amount * 60
                time_unit = "минут"
            elif time.endswith("h"):
                time_in_seconds = amount * 60 * 60
                time_unit = "часов"
            else:
                time_in_seconds = amount * 60 * 60 * 24
                time_unit = "дней"
            embed = discord.Embed(
                description=f"**{user.mention}** получил голосовой мут на `{amount} {time_unit}` от **{ctx.author}** по причине: `{reason}`",
                color=config.EMBED_COLOR
            )
            await user.add_roles(mute_role)
            await ctx.send(embed=embed)
        embed = discord.Embed(
            description=f"{user.mention} был размучен после {amount} {time_unit} голосового мута от **{ctx.author}**.",
            color=config.EMBED_COLOR
        )
        await asyncio.sleep(time_in_seconds)
        await user.remove_roles(mute_role)
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="mute",
        description="Выдать мут в чат на время",
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    @checks.not_blacklisted()
    @app_commands.describe(
        user="Пользователь, которого следует выдать мут.", 
        time="Время на которое выдать мут пользователя `s`, `m`, `h`, `d`", 
        reason="Причина, по которой пользователь должен быть замучен.")
    async def mute(self, ctx: commands.Context, user: discord.Member, time: str = None, *, reason: str = "Без причины") -> None:
        mute_role = discord.utils.get(ctx.guild.roles, name="Text Mute")
        if not mute_role:
            embed = discord.Embed(
                title="Ошибка",
                description="Роль для выдачи мута не найдена. Создайте роль `Text Mute`.",
                color=config.EMBED_COLOR
            )
            await ctx.send(embed=embed)
            return
        if user == ctx.author:
            embed = discord.Embed(
                description="Вы не можете выдать мут самому себе",
                color=config.EMBED_COLOR
            )
            await ctx.send(embed=embed)
            return
        if user.top_role.position >= ctx.author.top_role.position:
            embed = discord.Embed(
                description="Вы не можете выдать мут пользователю с ролью выше вашей.",
                color=config.EMBED_COLOR
            )
            await ctx.send(embed=embed)
            return
        if mute_role in user.roles:
            embed = discord.Embed(
                description=f"{user.mention} уже замучен.",
                color=config.EMBED_COLOR
            )
            await ctx.send(embed=embed)
            return
        if time:
            if len(time) < 2 or time[-1] not in "smhd":
                embed = discord.Embed(
                    title="Ошибка",
                    description="Некорректное время для мута.",
                    color=config.EMBED_COLOR
                )
                await ctx.send(embed=embed)
                return
            amount = int(time[:-1])
            if amount <= 0:
                embed = discord.Embed(
                    title="Ошибка",
                    description="Время не может быть меньше 1!",
                    color=config.EMBED_COLOR
                )
                await ctx.send(embed=embed)
                return
            if time.endswith("s"):
                time_in_seconds = amount
                time_unit = "секунд"
            elif time.endswith("m"):
                time_in_seconds = amount * 60
                time_unit = "минут"
            elif time.endswith("h"):
                time_in_seconds = amount * 60 * 60
                time_unit = "часов"
            else:
                time_in_seconds = amount * 60 * 60 * 24
                time_unit = "дней"
            embed = discord.Embed(
                description=f"**{user.mention}** получил мут в чат на `{amount} {time_unit}` от **{ctx.author}** по причине: `{reason}`",
                color=config.EMBED_COLOR
            )
            await user.add_roles(mute_role)
            await ctx.send(embed=embed)
        embed = discord.Embed(
            description=f"{user.mention} был размучен после {amount} {time_unit} текстового мута от **{ctx.author}**.",
            color=config.EMBED_COLOR
        )
        await asyncio.sleep(time_in_seconds)
        await user.remove_roles(mute_role)
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="nick",
        description="Изменить никнейм пользователя на сервере.",
    )
    @commands.has_permissions(manage_nicknames=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    @checks.not_blacklisted()
    @app_commands.describe(user="Пользователь, у которого должен быть новый псевдоним.", nickname="Новый псевдоним, который необходимо установить.")
    async def nick(self, context: Context, user: discord.User, *, nickname: str = None) -> None:
        """
        Сменить никнейм пользователя на сервере.

         :param context: Контекст гибридной команды.
         :param user: Пользователь, никнейм которого должен быть изменен.
         :param псевдоним: Новый псевдоним пользователя. По умолчанию установлено значение «Нет», что приведет к сбросу псевдонима.
        """
        member = context.guild.get_member(user.id) or await context.guild.fetch_member(user.id)
        try:
            await member.edit(nick=nickname)
            embed = discord.Embed(
                description=f"У **{member}** новый никнейм: **{nickname}**!",
                color=config.EMBED_COLOR
            )
            await context.send(embed=embed)
        except:
            embed = discord.Embed(
                description="Произошла ошибка при попытке изменить псевдоним пользователя. Убедитесь, что моя роль выше роли пользователя, которому вы хотите изменить никнейм.",
                color=config.EMBED_COLOR
            )
            await context.send(embed=embed)

    @commands.hybrid_command(
        name="clear",
        description="Удалить ряд сообщений.",
    )
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @checks.not_blacklisted()
    @app_commands.describe(amount="Количество сообщений, которые необходимо удалить.")
    async def clear(self, context: Context, amount: int) -> None:
        """
        Удалить ряд сообщений.

         :param context: Контекст гибридной команды.
         :param amount: Количество сообщений, которые необходимо удалить.
        """
        await context.send("Удаление сообщений...")  # Немного хакерский способ убедиться, что бот отвечает на взаимодействие и не получает ответ «Неизвестное взаимодействие».
        purged_messages = await context.channel.purge(limit=amount+1)
        embed = discord.Embed(
            description=f"**{context.author}** удалено **{len(purged_messages)-1}** сообщений!",
            color=config.EMBED_COLOR
        )
        await context.channel.send(embed=embed)

    @commands.hybrid_command(
        name="kick",
        description="Кикнуть пользователя с сервера.",
    )
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    @checks.not_blacklisted()
    @app_commands.describe(
        user="Пользователь, которого следует кикнуть.",
        reason="Причина, по которой пользователь должен быть кикнут.",
    )
    async def kick(
        self, context: Context, user: discord.User, *, reason: str = "Не указана"
    ) -> None:
        """
        Кикнуть пользователя с сервера.
        :param context: Контекст гибридной команды.
        :param user: Пользователь, которого нужно кикнуть с сервера.
        :param reason: Причина кика. По умолчанию "Не указано".
        """
        member = context.guild.get_member(user.id) or await context.guild.fetch_member(
            user.id
        )
        if member.guild_permissions.administrator:
            embed = discord.Embed(
                description="Пользователь имеет права администратора.", color=config.EMBED_COLOR
            )
            await context.send(embed=embed)
        else:
            try:
                embed = discord.Embed(
                    description=f"**{member}** был кикнут **{context.author}**!",
                    color=config.EMBED_COLOR,
                )
                embed.add_field(name="Причина:", value=reason)
                await context.send(embed=embed)
                try:
                    await member.send(
                        f"Вы были кикнуты модератором: **{context.guild.name}**!\nПричина: {reason}"
                    )
                except:
                    # Не удалось отправить сообщение в личных сообщениях пользователя
                    pass
                await member.kick(reason=reason)
            except:
                embed = discord.Embed(
                    description="Произошла ошибка при попытке исключить пользователя. Убедитесь, что моя роль выше роли пользователя, которого вы хотите исключить.",
                    color=config.EMBED_COLOR,
                )
                await context.send(embed=embed)

    @commands.hybrid_command(
        name="ban",
        description="Выдать бан на сервере.",
    )
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @checks.not_blacklisted()
    @app_commands.describe(user="Пользователь, которого следует забанить.", reason="Причина, по которой пользователь должен быть забанен.")
    async def ban(self, context: Context, user: discord.User, *, reason: str = "Без причин") -> None:
        """
        Bans a user from the server.

        :param context: The hybrid command context.
        :param user: The user that should be banned from the server.
        :param reason: The reason for the ban. Default is "Not specified".
        """
        member = context.guild.get_member(user.id) or await context.guild.fetch_member(user.id)
        try:
            if member.guild_permissions.administrator:
                embed = discord.Embed(
                    description="Пользователь имеет права администратора.",
                    color=config.EMBED_COLOR
                )
                await context.send(embed=embed)
            else:
                embed = discord.Embed(
                    description=f"**{member}** был забанен от **{context.author}**!",
                    color=config.EMBED_COLOR
                )
                embed.add_field(
                    name="Причина:",
                    value=reason
                )
                await context.send(embed=embed)
                try:
                    await member.send(f"Вы были забанены **{context.author}** от **{context.guild.name}**!\nПричина: {reason}")
                except:
                    # Couldn't send a message in the private messages of the user
                    pass
                await member.ban(reason=reason)
        except:
            embed = discord.Embed(
                title="Ошибка!",
                description="Произошла ошибка при попытке заблокировать пользователя. Убедитесь, что моя роль выше роли пользователя, которого вы хотите забанить.",
                color=config.EMBED_COLOR
            )
            await context.send(embed=embed)

    @commands.hybrid_group(
        name="warn",
        description="Управление предупреждениями пользователя на сервере.",
    )
    @commands.has_permissions(manage_messages=True)
    @checks.not_blacklisted()
    async def warn(self, context: Context) -> None:
        """
        Управление предупреждениями пользователя на сервере.

         :param context: Контекст гибридной команды.
        """
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                description="Укажите подкоманду.\n\n**Подкоманды:**\n`add` - Выдать пред пользователю\n`remove` - Удалить пред у пользователя.\n`list` - Список всех предов пользователя.",
                color=config.EMBED_COLOR
            )
            await context.send(embed=embed)

    @warn.command(
        name="add",
        description="Выдать предупреждение пользователю на сервере.",
    )
    @checks.not_blacklisted()
    @commands.has_permissions(manage_messages=True)
    @app_commands.describe(user="Пользователь, которого следует предупредить.", reason="Причина, по которой пользователь должен быть предупрежден.")
    async def warn_add(self, context: Context, user: discord.User, *, reason: str = "Без причины") -> None:
        """
        Предупреждает пользователя в его личных сообщениях.

         :param context: Контекст гибридной команды.
         :param user: Пользователь, которого следует предупредить.
         :param причина: Причина предупреждения. По умолчанию "Не указано".
        """
        member = context.guild.get_member(user.id) or await context.guild.fetch_member(user.id)
        total = await db_manager.add_warn(
            user.id, context.guild.id, context.author.id, reason)
        embed = discord.Embed(
            description=f"**{member}** получил предупреждение от **{context.author}**!\nВсего предупреждений у этого пользователя: {total}",
            color=config.EMBED_COLOR
        )
        embed.add_field(
            name="Причина:",
            value=reason
        )
        await context.send(embed=embed)
        try:
            await member.send(f"Вы были предупреждены **{context.author}** в **{context.guild.name}**!\nПричина: {reason}")
        except:
            # Не удалось отправить сообщение в личных сообщениях пользователя
            await context.send(f"{member.mention}, вас предупредил **{context.author}**!\nПричина: {reason}")

    @warn.command(
        name="remove",
        description="Удаляет предупреждение от пользователя на сервере.",
    )
    @checks.not_blacklisted()
    @commands.has_permissions(manage_messages=True)
    @app_commands.describe(user="Пользователь, предупреждение которого должно быть удалено.", warn_id="ID предупреждения, которое следует удалить.")
    async def warn_remove(self, context: Context, user: discord.User, warn_id: int) -> None:
        """
        Warns a user in his private messages.

        :param context: The hybrid command context.
        :param user: The user that should get their warning removed.
        :param warn_id: The ID of the warning that should be removed.
        """
        member = context.guild.get_member(user.id) or await context.guild.fetch_member(user.id)
        total = await db_manager.remove_warn(warn_id, user.id, context.guild.id)
        embed = discord.Embed(
            description=f"Вы удалили предупреждение **#{warn_id}** у пользователя: **{member}**!\nВсего предупреждений у этого пользователя: {total}",
            color=config.EMBED_COLOR
        )
        await context.send(embed=embed)

    @warn.command(
        name="list",
        description="Показывает предупреждения пользователя на сервере.",
    )
    @commands.has_guild_permissions(manage_messages=True)
    @checks.not_blacklisted()
    @app_commands.describe(user="Пользователь, от которого вы хотите посмотреть предупреждения.")
    async def warn_list(self, context: Context, user: discord.User):
        """
        Показывает предупреждения пользователя на сервере.

         :param context: Контекст гибридной команды.
         :param user: Пользователь, от которого вы хотите получать предупреждения.
        """
        warnings_list = await db_manager.get_warnings(user.id, context.guild.id)
        embed = discord.Embed(
            title=f"Предупреждения о {user}",
            color=config.EMBED_COLOR
        )
        description = ""
        if len(warnings_list) == 0:
            description = "У этого пользователя нет предупреждений."
        else:
            for warning in warnings_list:
                description += f"• Предупреждений <@{warning[2]}>: **{warning[3]}** (<t:{warning[4]}>) - ID преда #{warning[5]}\n"
        embed.description = description
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="id_ban",
        description="Забанить пользователя без необходимости присутствия пользователя на сервере.",
    )
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @checks.not_blacklisted()
    @app_commands.describe(user_id="ID пользователя, который должен быть забанен.", reason="Причина, по которой пользователь должен быть забанен.")
    async def id_ban(self, context: Context, user_id: str, *, reason: str = "Без причин") -> None:
        """
        Bans a user without the user having to be in the server.

        :param context: The hybrid command context.
        :param user_id: The ID of the user that should be banned.
        :param reason: The reason for the ban. Default is "Not specified".
        """
        try:
            await self.bot.http.ban(user_id, context.guild.id, reason=reason)
            user = self.bot.get_user(int(user_id)) or await self.bot.fetch_user(int(user_id))
            embed = discord.Embed(
                description=f"**{user}** (ID: {user_id}) был забанен от: **{context.author}**!",
                color=config.EMBED_COLOR
            )
            embed.add_field(
                name="Причина:",
                value=reason
            )
            await context.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                description="Произошла ошибка при попытке заблокировать пользователя. Убедитесь, что ID пользователя правильное!",
                color=config.EMBED_COLOR
            )
            await context.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CogModerator(bot))
