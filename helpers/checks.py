import os
import importlib.util
from typing import Callable, TypeVar

from discord.ext import commands

from exceptions import *
from helpers import db_manager

T = TypeVar("T")

def is_owner() -> Callable[[T], T]:
    """
    Это пользовательская проверка, чтобы узнать, является ли пользователь, выполняющий команду, владельцем бота.
    """

    async def predicate(context: commands.Context) -> bool:
        config_folder = os.path.join(os.path.dirname(__file__), "Settings")
        owner_file_path = os.path.join(config_folder, "config.py")

        spec = importlib.util.spec_from_file_location("OWNER", owner_file_path)
        owners_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(owners_module)

        if context.author.id not in owners_module.owners:
            raise UserNotOwner
        return True

    return commands.check(predicate)

def not_blacklisted() -> Callable[[T], T]:
    """
    Это пользовательская проверка, чтобы убедиться, что пользователь, выполняющий команду, не занесен в черный список.
    """

    async def predicate(context: commands.Context) -> bool:
        if await db_manager.is_blacklisted(context.author.id):
            raise UserBlacklisted
        return True

    return commands.check(predicate)