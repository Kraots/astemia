from disnake.ext import commands

from utils import Context

from main import Astemia


class ErrorHandler(commands.Cog):
    def __init__(self, bot: Astemia):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: Context, error):
        if hasattr(ctx.command, 'on_error'):
            return

        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        await ctx.reraise(error)


def setup(bot: Astemia):
    bot.add_cog(ErrorHandler(bot))
