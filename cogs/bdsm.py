from datetime import datetime
from asyncio import TimeoutError

import disnake
from disnake.ext import commands

import utils
from utils import Context, BDSM

from main import Astemia


class _BDSM(commands.Cog, name='BDSM'):
    """BDSM related commands."""

    def __init__(self, bot: Astemia):
        self.bot = bot

    @property
    def display_emoji(self) -> str:
        return '⛓️'

    @commands.group(invoke_without_command=True, case_insensitive=True, hidden=True)
    async def bdsm(self, ctx: Context):
        """Base command that shows all the other bdsm commands."""

        await ctx.send_help('BDSM')

    @bdsm.command(name='results', aliases=('result', 'show', 'check'))
    async def bdsm_res(self, ctx: Context, *, member: disnake.Member = None):
        """See the bdsm results of someone if they have it set.

        `member` **->** The member you want to see the bdsm results of. Defaults to yourself.
        """

        member = member or ctx.author

        entry: BDSM = await self.bot.db.get('bdsm', member.id)
        if entry is None:
            if member.id == ctx.author.id:
                return await ctx.reply('You did not set your bdsm results.')
            return await ctx.reply(f'{member.mention} did not set their bdsm results.')

        em = disnake.Embed(
            color=utils.blurple,
            title=f'Here\'s `{utils.format_name(member)}`\'s bdsm results',
            description=f'Results have been set on {utils.format_dt(entry.set_date, "F")} '
                        f'(`{utils.human_timedelta(entry.set_date, accuracy=7)}`)'
        )
        em.set_image(url=entry.result)
        em.set_footer(text=f'Requested By: {utils.format_name(ctx.author)}')

        await ctx.better_reply(embed=em)

    @bdsm.command(name='set', aliases=('add',))
    async def bdsm_set(self, ctx: Context):
        """Set or update your bdsm results.

        **NOTE:** This command can only be used in <#1097610036026548293>
        """

        if await ctx.check_channel() is False:
            return

        entry: BDSM = await self.bot.db.get('bdsm', ctx.author.id)
        if entry is not None:
            view = utils.ConfirmView(ctx)
            view.message = await ctx.reply(
                'You already have your bdsm results set, do you want to update it?',
                view=view
            )
            await view.wait()

            if view.response is False:
                return await view.message.edit(content='Your bdsm results haven\'t been updated.')

        await ctx.reply(
            'Please send the screenshot of your bdsm results.'
            '\n*Must be an image from your gallery.*'
        )
        try:
            res = await self.bot.wait_for(
                'message',
                check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id,
                timeout=180
            )

            try:
                result = res.attachments[0].url

                if entry is not None:
                    entry.result = result
                    entry.set_date = datetime.utcnow()
                    await entry.commit()
                    return await res.reply(
                        'Succesfully updated your bdsm result. '
                        'To check your bdsm results or others, '
                        'you can type `!bdsm results <member>`.'
                    )

                await self.bot.db.add('bdsm', BDSM(
                    id=ctx.author.id,
                    result=result,
                    set_date=datetime.utcnow()
                ))

                return await res.reply(
                    'Succesfully set your bdsm result. '
                    'To check your bdsm results or others, '
                    'you can type `!bdsm results <member>`.'
                )

            except Exception:
                return await res.reply('You must send an image from your gallery, not an url.')

        except TimeoutError:
            await ctx.reply(
                'You ran out of time, type the command again to set your bdsm results.'
            )

    @bdsm.command(name='remove', aliases=('delete',))
    async def bdsm_remove(self, ctx: Context):
        """Remove your bdsm results if you have them set."""

        entry: BDSM = await self.bot.db.get('bdsm', ctx.author.id)
        if entry is None:
            return await ctx.reply('You did not set your bdsm results.')

        view = utils.ConfirmView(ctx)
        view.message = await ctx.reply(
            'Are you sure you want to remove your bdsm results?',
            view=view
        )
        await view.wait()
        if view.response is False:
            return await view.message.edit(content='Did not remove your bdsm results.')

        await self.bot.db.delete('bdsm', {'_id': entry.pk})
        await view.message.edit(content='Successfully removed your bdsm results.')

    @bdsm.command(name='test', aliases=('url',))
    async def bdsm_test(self, ctx: Context):
        """The url to the bdsm test."""

        await ctx.better_reply(
            'Click the link below to take your bdsm test (and please choose '
            'the long version for better accuracy): \nhttps://bdsmtest.org/prelims'
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        if member.guild.id != 1097610034701144144:
            return

        await self.bot.db.delete('bdsm', {'_id': member.id})


def setup(bot: Astemia):
    bot.add_cog(_BDSM(bot))
