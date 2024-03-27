import platform
import random
import datetime
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

from typing import List, Dict, Union, Optional

from helpers import checks
from Settings import config

class CogGeneral(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot
        self.api_urls = {
            'kiss': 'https://nekos.life/api/v2/img/kiss',
            'slap': 'https://nekos.life/api/v2/img/slap',
            'hug': 'https://nekos.life/api/v2/img/hug'
        }

    async def _get_action_image(self, action):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.api_urls[action]) as response:
                    data = await response.json()
                return data['url']
            except Exception as e:
                print(f"Ошибка при получении {action} изображение: {e}")
                return None

    @commands.hybrid_command(
    name="kiss",
    description="Поцеовать человека"
    )
    @commands.has_permissions(manage_messages=True)
    @checks.not_blacklisted()
    async def kiss(self, ctx, user: discord.User, *, reason: str = "из-за любви"):
        image_url = await self._get_action_image('kiss')
        if image_url:
            embed = discord.Embed(
                title="💋⠀**Поцелуй**",
            description=f"{ctx.author.mention} поцеловал(а) {user.mention}",
                color=config.EMBED_COLOR
            ).add_field(
                name="**Причина**",
                value=reason,
                inline=False
            )
            embed.set_image(url=image_url)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Произошла ошибка при получении изображения поцелуя.")

    @commands.hybrid_command(
    name="slap",
    description="Ударить человека"
    )
    @commands.has_permissions(manage_messages=True)
    @checks.not_blacklisted()
    async def slap(self, ctx, user: discord.User, *, reason: str = "за плохое поведение"):
        image_url = await self._get_action_image('slap')
        if image_url:
            embed = discord.Embed(
                title="👋⠀**Пощечина**",
                description=f"{ctx.author.mention} ударил(а) {user.mention}",
                color=config.EMBED_COLOR
            ).add_field(
                name="**Причина**",
                value=reason,
                inline=False
            )
            embed.set_image(url=image_url)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Произошла ошибка при получении изображения пощечины.")

    @commands.hybrid_command(
    name="hug",
    description="Обнять человека"
    )
    @commands.has_permissions(manage_messages=True)
    @checks.not_blacklisted()
    async def hug(self, ctx, user: discord.User, *, reason: str = "из-за дружбы"):
        image_url = await self._get_action_image('hug')
        if image_url:
            embed = discord.Embed(
                title="🤗⠀**Объятие**",
                description=f"{ctx.author.mention} обнял(а) {user.mention}",
                color=config.EMBED_COLOR
            ).add_field(
                name="**Причина**",
                value=reason,
                inline=False
            )
            embed.set_image(url=image_url)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Произошла ошибка при получении изображения обнимание.")

    @commands.hybrid_command(
    name="rand",
    aliases=["r"],
    description="Получить произвольное число"
    )
    @commands.has_permissions(manage_messages=True)
    @checks.not_blacklisted()
    async def rand(self, ctx, a: Optional[int] = 0, b: Optional[int] = None):
        if b is None:
            b = a
            a = 0
        if a > b:
            a, b = b, a
        await ctx.send(random.randint(a, b))

    @commands.hybrid_command(
    name="inviteinfo",
    aliases=["invite", "linkinfo"],
    description="Информация о ссылке-приглашении"
    )
    @commands.has_permissions(manage_messages=True)
    @checks.not_blacklisted()
    async def inviteinfo(self, ctx: commands.Context, invite_code: str):
        """
        Показывает информацию о ссылке-приглашении, включая данные о сервере аналогично команде "serverinfo" если бот есть на этом сервере.

        Использование:
            {prefix}inviteinfo <invite_code>

        Пример:
            {prefix}inviteinfo ABCD1234
        """
        server_embed = None
        try:
            invite = await self.bot.fetch_invite(invite_code)
        except discord.errors.NotFound:
            return await ctx.send(f"Ссылка-приглашение `{invite_code}` не найдена или недействительна.")

        if invite.guild is not None:
            server_cog = self.bot.get_cog("server")
        if server_cog is not None:
            server_embed = await server_cog._generate_server_info_embed(invite.guild)

        if invite.max_age is not None:
            created_at_str = invite.created_at.strftime('%Y-%m-%d %H:%M:%S')
        else:
            created_at_str = "Неизвестно"

        if invite.expires_at is not None:
            expires_at_str = invite.expires_at.strftime('%Y-%m-%d %H:%M:%S')
        else:
            expires_at_str = "Неограничено"

        # Проверяем реальное количество использований ссылки-приглашения
        invite_uses = invite.uses
        if invite_uses is None:
            invite_uses = 0

        embed = discord.Embed(
            title=f"Информация о ссылке-приглашении {invite.url}",
            color=config.EMBED_COLOR
        )
        embed.add_field(name="Код ссылки", value=invite_code)
        embed.add_field(name="Максимальное количество пользователей", value=invite.max_age)
        embed.add_field(name="Количество использований", value=invite_uses)
        embed.add_field(name="Создатель", value=invite.inviter)
        embed.add_field(name="Время создания", value=created_at_str)
        embed.add_field(name="Время действия", value=expires_at_str)
        if server_embed:
            embed.add_field(
                name="Сервер", 
                value=f"[{invite.guild.name}]({invite.guild.icon_url})", 
                inline=False
            )
            embed.add_field(
                name="Дополнительная информация о сервере", 
                value=f"{server_embed.description}\n{server_embed.fields[0].value}\n{server_embed.fields[1].value}"
            )
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="ping",
        description="Проверить пинг бота",
    )
    @commands.has_permissions(manage_messages=True)
    @checks.not_blacklisted()
    async def ping(self, context: Context) -> None:
        """
        Проверьте, жив ли бот.

        :param context: Tконтекст гибридной команды.
        """
        embed = discord.Embed(
            title="🏓 Понг!",
            description=f"Задержка бота {round(self.bot.latency * 1000)}ms.",
            color=config.EMBED_COLOR
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="avatar",
        description="Отображает фото профиля пользователя",
    )
    @checks.not_blacklisted()
    async def avatar(self, ctx: commands.Context, member: Optional[discord.Member] = None) -> None:
        if not member:
            member = ctx.author

        if member.avatar:
            avatar_url = member.avatar.url
            if member.avatar.is_animated():
                await ctx.send(f"{member}'s анимированный аватар: {avatar_url}")
            else:
                await ctx.send(f"{member}'s аватар: {avatar_url}")
        else:
            await ctx.send(f"{member} не имеет аватара.")

    @commands.hybrid_command(
    name="8ball",
    description="Задайте любой вопрос боту.",
    )
    @commands.has_permissions(manage_messages=True)
    @checks.not_blacklisted()
    @app_commands.describe(question="Вопрос, который вы хотите задать.")
    async def eight_ball(self, ctx, *, question: str) -> None:
        """
        Задайте любой вопрос боту.

        :param context: Контекст гибридной команды.
        :param question: Вопрос, который должен задать пользователь.
        """
        # Находим упоминания пользователей в вопросе и экранируем их
        escaped_question = discord.utils.escape_mentions(question)

        answers = ["Это точно.", "Это определенно так.", "Вы можете на это положиться.", "Без сомнения.",
                   "Да, безусловно.", "Как я вижу, да.", "Скорее всего.", "Перспектива хорошая.", "Да.",
                   "Знаки указывают на да.", "Ответ туманный, попробуйте еще раз.", "Спросите позже, я на педикюр.", "Лучше не говорить тебе сейчас.",
                   "Не могу предсказать сейчас.", "Сконцентрируйтесь и спросите позже.", "Не рассчитывайте на это.", "Мой ответ - нет.",
                   "Мои источники говорят, что нет.", "Перспективы не очень.", "Очень сомнительно."]
        embed = discord.Embed(
            title="🎱 8ball",
            description="Смотрите ответ на свой вопрос!",
            color=config.EMBED_COLOR
        )
        embed.add_field(
            name="💬 Ваш вопрос",
            value=f"`{escaped_question}`",
            inline=False
        )

        # Ищем упоминания пользователей в вопросе и добавляем их к ответу
        user_mentions = ctx.message.mentions
        if user_mentions:
            mentioned_users = [user.mention for user in user_mentions]
            user_string = ', '.join(mentioned_users)
            embed.add_field(
                name="👥 Упомянутые пользователи",
                value=user_string,
                inline=False
            )

        embed.add_field(
            name="🤖 Ответ бота",
            value=f"`{random.choice(answers)}`",
            inline=False
        )
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(CogGeneral(bot))