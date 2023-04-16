from datetime import datetime

import disnake
from disnake.ext import commands

import utils
from utils import Context, Marriage

from main import Astemia


class Marriages(commands.Cog):
    """Marriage commands."""
    def __init__(self, bot: Astemia):
        self.bot = bot

    @property
    def display_emoji(self) -> str:
        return '❤️'

    @commands.command()
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def marry(self, ctx: Context, *, member: disnake.Member):
        """Marry the member if they want to and if you're/they're not taken by somebody else already.
        `member` **->** The member you wish to marry. You can either ping them, give their discord id, or just type in their username
        """

        if ctx.author == member:
            return await ctx.reply(f'{ctx.denial} You cannot marry yourself.')
        elif member.bot and ctx.author.id != self.bot._owner_id:
            return await ctx.reply(f'{ctx.denial} You cannot marry bots.')

        data1: Marriage = await self.bot.db.get('marriage', ctx.author.id)
        if data1 and data1.married_to != 0:
            mem = ctx.ukiyo.get_member(data1.married_to)
            return await ctx.reply(f'{ctx.denial} You are already married to {mem.mention}')
        elif data1 and member.id in data1.adoptions:
            return await ctx.reply(
                f'{ctx.denial} You cannot marry the person that you adopted.'
            )

        data2: Marriage = await self.bot.db.get('marriage', member.id)
        if data2 and data2.married_to != 0:
            mem = ctx.ukiyo.get_member(data2.married_to)
            return await ctx.reply(f'{ctx.denial} `{utils.format_name(member)}` is already married to {mem.mention}')
        elif data2 and ctx.author.id in data2.adoptions:
            return await ctx.reply(
                f'{ctx.denial} You cannot marry the person that adopted you.'
            )
        elif member.id == self.bot._owner_id:
            return await ctx.reply(f'{ctx.denial} No.')

        view = utils.ConfirmView(ctx, f'{ctx.denial} {member.mention} Did not react in time.', member)
        view.message = msg = await ctx.send(f'{member.mention} do you want to marry {ctx.author.mention}?', view=view)
        await view.wait()
        if view.response is True:
            now = datetime.utcnow()

            if data1 is None:
                await self.bot.db.add('marriages', Marriage(
                    id=ctx.author.id,
                    married_to=0,
                    married_since=utils.FIRST_JANUARY_1970,
                    adoptions=[]
                ))
                data1 = await self.bot.db.get('marriage', ctx.author.id)

            if data2 is None:
                await self.bot.db.add('marriages', Marriage(
                    id=member.id,
                    married_to=0,
                    married_since=utils.FIRST_JANUARY_1970,
                    adoptions=[]
                ))
                data2 = await self.bot.db.get('marriage', member.id)

            data1.married_to = member.id
            data1.married_since = now
            await data1.commit()

            data2.married_to = ctx.author.id
            data2.married_since = now
            await data2.commit()

            await ctx.send(f'`{ctx.author.display_name}` married `{member.display_name}`!!! :heart: :tada: :tada:')
            await utils.try_delete(msg)

        elif view.response is False:
            await ctx.send(f'`{member.display_name}` does not want to marry you. {ctx.author.mention} :pensive: :fist:')
            await utils.try_delete(msg)

    @commands.command()
    @commands.max_concurrency(1, commands.BucketType.user)
    async def divorce(self, ctx: Context):
        """Divorce the person you're married with in case you're married with anybody."""

        data: Marriage = await self.bot.db.get('marriage', ctx.author.id)

        if data is None or data.married_to == 0:
            return await ctx.reply(f'{ctx.denial} You are not married to anyone.')

        else:
            usr = ctx.ukiyo.get_member(data.married_to)

            view = utils.ConfirmView(ctx, f'{ctx.author.mention} Did not react in time.')
            view.message = msg = await ctx.reply(f'Are you sure you want to divorce {usr.mention}?', view=view)
            await view.wait()
            if view.response is True:
                mem: Marriage = await self.bot.db.get('marriage', usr.id)
                await self.bot.db.delete('marriages', {'_id': data.pk})
                await self.bot.db.delete('marriages', {'_id': mem.pk})

                e = f'You divorced {usr.mention} that you have been married ' \
                    f'since {utils.format_dt(data.married_since, "F")} ' \
                    f'(`{utils.human_timedelta(data.married_since)}`)'
                return await msg.edit(content=e, view=view)

            elif view.response is False:
                e = f'You did not divorce {usr.mention}'
                return await msg.edit(content=e, view=view)

    @commands.command(aliases=('marriedwho', 'marriedsince'))
    async def marriage(self, ctx: Context, *, member: disnake.Member = None):
        """See who, who, the date and how much it's been since the member married their partner if they have one.
        `member` **->** The member you want to see who they are married with. If you want to see who you married, you can ignore this.
        """

        member = member or ctx.author
        data: Marriage = await self.bot.db.get('marriage', member.id)
        if data is None or data.married_to == 0:
            if member == ctx.author:
                i = f'{ctx.denial} You\'re not married to anyone.'
                fn = ctx.reply
            else:
                i = f'{ctx.denial} {member.mention} is not married to anyone.'
                fn = ctx.better_reply
            return await fn(i)

        mem = ctx.ukiyo.get_member(data.married_to)
        em = disnake.Embed(title=f'Married to `{mem.display_name}`', colour=utils.red)
        if member == ctx.author:
            i = 'You\'re married to'
            fn = ctx.reply
        else:
            i = f'{member.mention} is married to'
            fn = ctx.better_reply
        em.description = f'{i} {mem.mention} ' \
                         f'since {utils.format_dt(data.married_since, "F")} ' \
                         f'(`{utils.human_timedelta(data.married_since, accuracy=6)}`)'
        await fn(embed=em)


    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        if member.guild.id != 1095130822610268180:
            return

        await self.bot.db.delete('marriage', {'_id': member.id})
        await self.bot.db.delete('marriage', {'married_to': member.id})


def setup(bot: Astemia):
    bot.add_cog(Marriages(bot))
