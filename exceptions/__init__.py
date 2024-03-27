from discord.ext import commands


class UserBlacklisted(commands.CheckFailure):
    """
    Возникает, когда пользователь пытается что-то сделать, но попадает в черный список.
    """

    def __init__(self, message="Пользователь внесен в черный список!"):
        self.message = message
        super().__init__(self.message)


class UserNotOwner(commands.CheckFailure):
    """
    Возникает, когда пользователь пытается что-то сделать, но не является владельцем бота.
    """

    def __init__(self, message="Пользователь не является владельцем бота!"):
        self.message = message
        super().__init__(self.message)
