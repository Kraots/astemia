import disnake
from disnake.ext import commands

import utils
from utils import Context

from main import Astemia


class Actions(commands.Cog):
    """Action commands."""
    def __init__(self, bot: Astemia):
        self.bot = bot

    @property
    def display_emoji(self) -> str:
        return '<:hug:1097656668462006434>'

    @commands.command(name='huggles')
    async def _huggles(self, ctx: Context, members: commands.Greedy[disnake.Member] = None):
        """Give somebody a hug ❤️

        `members` **->** The people you want to hug. Can be more than just one, or none.
        """

        mems = ' '.join([m.mention for m in members]) if members else None
        em = disnake.Embed(color=utils.red)
        em.set_image(
            url='https://cdn.discordapp.com/attachments/938411306762002456/938475660601602159/huggles.gif'
        )

        await ctx.reply(mems, embed=em)

    @commands.command(name='pat')
    async def _pat(self, ctx: Context, members: commands.Greedy[disnake.Member] = None):
        """Give somebody a pat ❤️

        `members` **->** The people you want to pat. Can be more than just one, or none.
        """

        mems = ' '.join([m.mention for m in members]) if members else None
        em = disnake.Embed(color=utils.red)
        em.set_image(
            url='https://cdn.discordapp.com/attachments/938411306762002456/938475661209767947/pat.gif'
        )

        await ctx.reply(mems, embed=em)

    @commands.command(name='slap')
    async def _slap(self, ctx: Context, members: commands.Greedy[disnake.Member] = None):
        """Give somebody a slap <:slap:1097656683376947260>

        `members` **->** The people you want to slap. Can be more than just one, or none.
        """

        mems = []
        if members is not None:
            for mem in members:
                if mem.id == self.bot._owner_id:
                    mem = ctx.author
                mems.append(mem.mention)
        mems = ' '.join(mems) if mems else None

        em = disnake.Embed(color=utils.red)
        em.set_image(
            url='https://cdn.discordapp.com/attachments/938411306762002456/938475660962299974/slap.gif'
        )

        await ctx.reply(mems, embed=em)

    @commands.command(name='kill')
    async def _kill(self, ctx: Context, members: commands.Greedy[disnake.Member] = None):
        """Kill somebody 🪦

        `members` **->** The people you want to kill. Can be more than just one, or none.
        """

        mems = []
        if members is not None:
            for mem in members:
                if mem.id == self.bot._owner_id:
                    mem = ctx.author
                mems.append(mem.mention)
        mems = ' '.join(mems) if mems else None

        em = disnake.Embed(color=utils.red)
        em.set_image(
            url='https://cdn.discordapp.com/attachments/938411306762002456/938475661490815006/kill.gif'
        )

        await ctx.reply(mems, embed=em)

    @commands.command(name='bonk')
    async def _bonk(self, ctx: Context, *, user: disnake.User):
        """Bonk someone.

        `user` **->** The user you want to bonk.
        """

        user = ctx.author if user.id == self.bot._owner_id else user

        await ctx.message.add_reaction(ctx.thumb)
        file = await utils.bonk_gif(user)
        em = disnake.Embed(color=utils.red)
        em.set_image(file=file)

        await ctx.reply(user.mention, embed=em)


def setup(bot: Astemia):
    bot.add_cog(Actions(bot))
