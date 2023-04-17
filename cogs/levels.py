import matplotlib.pyplot as plt
from datetime import datetime

import disnake
from disnake.ext import commands

import utils
from utils import Level, Context, Stats

from main import Astemia


class Levels(commands.Cog):
    """Level and message related commands."""
    def __init__(self, bot: Astemia):
        self.bot = bot

    @property
    def display_emoji(self) -> disnake.PartialEmoji:
        return disnake.PartialEmoji(name='super_mario_green_shroom', id=938412194700341350)

    @commands.Cog.listener('on_message')
    async def update_data(self, message: disnake.Message):
        if not message.author.bot and message.guild:
            data: Level = await self.bot.db.get('level', message.author.id)
            if data is None:
                return await self.bot.db.add('levels', Level(id=message.author.id, xp=5, messages_count=1))
            if message.author.id == self.bot._owner_id:
                data.xp += 30
            else:
                if message.channel.id not in (utils.Channels.bots, utils.Channels.memes):
                    if utils.ExtraRoles.server_booster in (r.id for r in message.author.roles):
                        data.xp += 10
                    elif utils.ExtraRoles.special_booster in (r.id for r in message.author.roles):
                        data.xp += 20
                    else:
                        data.xp += 5
            data.messages_count += 1
            await data.commit()

            lvl = 0
            xp = data.xp
            while True:
                if xp < ((50 * (lvl**2)) + (50 * (lvl - 1))):
                    break
                lvl += 1
            xp -= ((50 * ((lvl - 1)**2)) + (50 * (lvl - 1)))
            if xp < 0:
                lvl = lvl - 1

            if message.author.id != self.bot._owner_id:
                if lvl >= 10:
                    guild = self.bot.get_guild(1097610034701144144)
                    role = guild.get_role(1097616298692845628)

                    if role.id not in [r.id for r in message.author.roles]:
                        roles = list(message.author.roles) + [role]
                        await message.author.edit(roles=roles)

                        await utils.try_dm(
                            message.author,
                            content='Congratulations of reaching level **10** in `Astemia`, '
                                    'you have now unlocked the role **Pic Perms** which '
                                    'allows you to send gifs and images/videos in every channel '
                                    'you have access to chat in.'
                        )

    @commands.group(
        name='level', invoke_without_command=True, case_insensitive=True, aliases=('rank',)
    )
    async def level_cmd(self, ctx: Context, *, member: disnake.Member = None):
        """Check your current level or somebody else's.

        `member` **->** The member you want to see the level of. If you want to see your own, you can ignore this since it defaults to yourself.

        **NOTE:** This command can only be used in <#1097610036026548293>
        """

        if await ctx.check_channel() is False:
            return

        member = member or ctx.author
        if member.bot:
            return await ctx.better_reply(f'{ctx.denial} Bot\'s do not have levels!')
        data: Level = await self.bot.db.get('level', member.id)
        if data is None:
            return await ctx.better_reply(f'{ctx.denial} User not in the database!')

        rank = 0
        async for _rank in Level.find().sort('xp', -1):
            rank += 1
            if data.id == _rank.id:
                break

        lvl = 0
        xp = data.xp
        while True:
            if xp < ((50 * (lvl**2)) + (50 * (lvl - 1))):
                break
            lvl += 1
        xp -= ((50 * ((lvl - 1)**2)) + (50 * (lvl - 1)))
        if xp < 0:
            lvl = lvl - 1
            xp = data.xp
            xp -= ((50 * ((lvl - 1)**2)) + (50 * (lvl - 1)))
        if str(xp).endswith(".0"):
            x = str(xp).replace(".0", "")
            x = int(x)
        else:
            x = int(xp)

        current_xp = x
        needed_xp = int(200 * ((1 / 2) * lvl))
        percent = round(float(current_xp * 100 / needed_xp), 2)
        members_count = len([m for m in ctx.astemia.members if not m.bot])

        rank_card = await (await utils.run_in_executor(utils.create_rank_card)(
            member, lvl, rank, members_count, current_xp, needed_xp, percent
        ))
        await ctx.better_reply(file=rank_card)

    @level_cmd.command(name='set')
    @utils.is_owner()
    async def level_set(self, ctx: Context, level: int, *, member: disnake.Member = None):
        """Set the level for somebody.

        `level` **->** The level to set.
        `member` **->** The member to set the level for.
        """

        member = member or ctx.author
        if await ctx.check_perms(member) is False:
            return

        if level < 0:
            return await ctx.reply(f'{ctx.denial} Level cannot be less than `0`')

        xp = ((50 * ((level - 1)**2)) + (50 * (level - 1)))
        data: Level = await self.bot.db.get('level', member.id)
        if data is not None:
            data.xp = xp
            await data.commit()
            return await ctx.reply(f'Successfully set `{utils.format_name(member)}` to level **{level}**')
        await ctx.reply(f'{ctx.denial} Member not in the database.')

    @level_cmd.command(name='leaderboard', aliases=('lb', 'top',))
    async def level_top(self, ctx: Context):
        """See the top people with the highest levels.

        **NOTE:** This command can only be used in <#1097610036026548293>
        """

        if await ctx.check_channel() is False:
            return

        entries = []
        index = 0
        top_3_emojis = {1: '🥇', 2: '🥈', 3: '🥉'}
        level_entries = await self.bot.db.find_sorted('level', 'xp', 0)
        for entry in level_entries:
            entry: Level

            index += 1
            lvl = 0
            while True:
                if entry.xp < ((50 * (lvl**2)) + (50 * (lvl - 1))):
                    break
                lvl += 1
            user = ctx.astemia.get_member(entry.id)
            if index in (1, 2, 3):
                place = top_3_emojis[index]
            else:
                place = f'`#{index:,}`'

            if user == ctx.author:
                to_append = (f"**{place} {user.display_name} (YOU)**", f"Level: `{lvl}`\nTotal XP: `{entry.xp:,}`")
                entries.append(to_append)
            else:
                to_append = (f"{place} {user.display_name}", f"Level: `{lvl}`\nTotal XP: `{entry.xp:,}`")
                entries.append(to_append)

        source = utils.FieldPageSource(entries, per_page=10)
        source.embed.title = 'Rank Leaderboard'
        pages = utils.RoboPages(source, ctx=ctx)
        await pages.start()

    @commands.group(
        name='messages', invoke_without_command=True, case_insensitive=True, aliases=(
            'msg', 'message', 'm')
    )
    async def _msgs(self, ctx: Context, *, member: disnake.Member = None):
        """Check yours or somebody else's total messages.

        `member` **->** The member you want to see the total messages of. If you want to see your own, you can ignore this since it defaults to yourself.
        """

        member = member or ctx.author

        user_db: Level = await self.bot.db.get('level', member.id)
        if user_db is None:
            return await ctx.better_reply(f'`{member.display_name}` sent no messages.')
        rank = 0
        entries = await self.bot.db.find_sorted('level', 'messages_count', 0)
        for entry in entries:
            rank += 1
            if entry.id == user_db.id:
                break
        em = disnake.Embed(color=utils.blurple)
        em.set_author(name=f'{member.display_name}\'s message stats', icon_url=member.display_avatar)
        em.add_field(name='Total Messages', value=f"`{user_db.messages_count:,}`")
        em.add_field(name='Rank', value=f"`#{rank:,}`")
        em.set_footer(text=f'Requested by: {utils.format_name(ctx.author)}')
        await ctx.better_reply(embed=em)

    @_msgs.command(name='leaderboard', aliases=('top', 'lb',))
    async def msg_top(self, ctx: Context):
        """See a top of most active users."""

        index = 0
        data = []
        top_3_emojis = {1: '🥇', 2: '🥈', 3: '🥉'}
        entries = await self.bot.db.find_sorted('level', 'messages_count', 0)

        for entry in entries:
            entry: Level

            if entry.messages_count != 0:
                index += 1
                mem = ctx.astemia.get_member(entry.id)
                if index in (1, 2, 3):
                    place = top_3_emojis[index]
                else:
                    place = f'`#{index:,}`'
                if mem == ctx.author:
                    to_append = (f'**{place} {mem.display_name} (YOU)**', f'**{entry.messages_count:,}** messages')
                    data.append(to_append)
                else:
                    to_append = (f'{place} {mem.display_name}', f'**{entry.messages_count:,}** messages')
                    data.append(to_append)

        source = utils.FieldPageSource(data, per_page=10)
        source.embed.title = 'Top Most Active Users'
        pages = utils.RoboPages(source, ctx=ctx)
        await pages.start()

    @_msgs.command(name='add')
    @utils.is_admin()
    async def msg_add(self, ctx: Context, member: disnake.Member, *, amount: str):
        """Add a certain amount of messages for the member.

        `member` **->** The member to add the amount of messages messages to.
        `amount` **->** The amount of messages to add.
        """

        if await ctx.check_perms(member) is False:
            return
        usr_db: Level = await self.bot.db.get('level', member.id)
        if usr_db is None:
            return await ctx.reply(f'{ctx.denial} User not in the database.')

        try:
            amount = utils.format_amount(amount)
            amount = int(amount)
        except ValueError:
            return await ctx.reply(f'{ctx.denial} The amount must be an integer.')

        usr_db.messages_count += amount
        await usr_db.commit()
        await ctx.send(content=f'Added `{amount:,}` messages to {member.mention}')

    @_msgs.command(name='set')
    @utils.is_admin()
    async def msg_set(self, ctx: Context, member: disnake.Member, *, amount: str):
        """Set the amount of messages for the member.

        `member` **->** The member to set the amount of messages messages to.
        `amount` **->** The amount of messages to set.
        """

        if await ctx.check_perms(member) is False:
            return

        usr_db: Level = await self.bot.db.get('level', member.id)
        if usr_db is None:
            return await ctx.reply(f'{ctx.denial} User not in the database.')

        try:
            amount = utils.format_amount(amount)
            amount = int(amount)
        except ValueError:
            return await ctx.reply(f'{ctx.denial} The amount must be an integer.')

        usr_db.messages_count = amount
        await usr_db.commit()
        await ctx.send(content=f'Set the amount of messages for {member.mention} to `{amount:,}` messages.')

    @_msgs.command(name='reset')
    @utils.is_admin()
    async def msg_reset(self, ctx: Context, member: disnake.Member):
        """Reset the amount of total messages for the member.

        `member` **->** The member for who to reset the total messages count for.
        """

        if await ctx.check_perms(member) is False:
            return

        usr_db: Level = await self.bot.db.get('level', member.id)
        if usr_db is None:
            return await ctx.reply(f'{ctx.denial} User not in the database.')

        view = utils.ConfirmView(ctx, f"{ctx.author.mention} Did not react in time.")
        view.message = msg = await ctx.send(
            f"Are you sure you want to reset the total message count for member {member.mention}?",
            view=view
        )
        await view.wait()
        if view.response is True:
            usr_db.messages_count = 0
            await usr_db.commit()
            return await msg.edit(
                content=f'The total message count for member **{utils.format_name(member)}** has been reset successfully.',
            )

        elif view.response is False:
            return await msg.edit(
                content=f"Command to reset the message count for user `{utils.format_name(member)}` has been cancelled.",
            )

    async def create_graph(self, user_id: int) -> dict[str, disnake.File]:
        """Creates the graph.

        Parameters
        ----------
            user_id: :class:`int`
                The id to search for in the db. (0 for the server data)

        Return
        ------
            :class:`dict`[:class:`disnake.File`]
        """

        async def create(days: list[str], amounts: list[str], measurement: str):
            if len(days) > 12:
                fig, ax = await utils.run_in_executor(plt.subplots)(figsize=(30, 30))
            elif len(days) > 7:
                fig, ax = await utils.run_in_executor(plt.subplots)(figsize=(15, 15))
            elif len(days) > 1:
                fig, ax = await utils.run_in_executor(plt.subplots)(figsize=(10, 10))
            else:
                fig, ax = await utils.run_in_executor(plt.subplots)()

            rect = await utils.run_in_executor(ax.bar)(x=days, height=amounts)
            await utils.run_in_executor(ax.bar_label)(rect, labels=amounts)

            await utils.run_in_executor(ax.set)(ylabel='messages', xlabel=measurement)
            return fig

        user_data: Stats = await self.bot.db.get('stats', user_id)
        user_daily = user_data.daily_messages.copy()
        user_daily.pop('reset_when')
        user_weekly = user_data.weekly_messages.copy()
        user_weekly.pop('reset_when')
        user_monthly = user_data.monthly_messages.copy()
        user_monthly.pop('reset_when')
        user_yearly = user_data.yearly_messages.copy()
        user_yearly.pop('reset_when')

        server_data: Stats = await self.bot.db.get('stats', 0)
        server_daily = server_data.daily_messages.copy()
        server_daily.pop('reset_when')
        server_weekly = server_data.weekly_messages.copy()
        server_weekly.pop('reset_when')
        server_monthly = server_data.monthly_messages.copy()
        server_monthly.pop('reset_when')
        server_yearly = server_data.yearly_messages.copy()
        server_yearly.pop('reset_when')

        user_daily_fig = await create(['Today'], [user_daily['Today']], 'Daily')
        user_daily_fig.savefig(f'stats_chart/user-daily-{user_id}.png', bbox_inches='tight')
        plt.close(user_daily_fig)

        weeks = [k for k in user_weekly.keys()]
        week_amount = [v for v in user_weekly.values()]
        user_weekly_fig = await create(weeks, week_amount, 'Weekly')
        user_weekly_fig.savefig(f'stats_chart/user-weekly-{user_id}.png', bbox_inches='tight')
        plt.close(user_weekly_fig)

        months = [k for k in user_monthly.keys()]
        month_amount = [v for v in user_monthly.values()]
        user_monthly_fig = await create(months, month_amount, 'Monthly')
        user_monthly_fig.savefig(f'stats_chart/user-monthly-{user_id}.png', bbox_inches='tight')
        plt.close(user_monthly_fig)

        years = [k for k in user_yearly.keys()]
        year_amount = [v for v in user_yearly.values()]
        user_yearly_fig = await create(years, year_amount, 'Yearly')
        user_yearly_fig.savefig(f'stats_chart/user-yearly-{user_id}.png', bbox_inches='tight')
        plt.close(user_yearly_fig)

        server_daily_fig = await create(['Today'], [server_daily['Today']], 'Daily')
        server_daily_fig.savefig('stats_chart/server-daily.png', bbox_inches='tight')
        plt.close(server_daily_fig)

        weeks = [k for k in server_weekly.keys()]
        week_amount = [v for v in server_weekly.values()]
        server_weekly_fig = await create(weeks, week_amount, 'Weekly')
        server_weekly_fig.savefig('stats_chart/server-weekly.png', bbox_inches='tight')
        plt.close(server_weekly_fig)

        months = [k for k in server_monthly.keys()]
        month_amount = [v for v in server_monthly.values()]
        server_monthly_fig = await create(months, month_amount, 'Monthly')
        server_monthly_fig.savefig('stats_chart/server-monthly.png', bbox_inches='tight')
        plt.close(server_monthly_fig)

        years = [k for k in server_yearly.keys()]
        year_amount = [v for v in server_yearly.values()]
        server_yearly_fig = await create(years, year_amount, 'Yearly')
        server_yearly_fig.savefig('stats_chart/server-yearly.png', bbox_inches='tight')
        plt.close(server_yearly_fig)

    @_msgs.command(name='stats')
    async def show_stats(self, ctx: Context, *, member: disnake.Member = None):
        """Shows charts of message stats.

        `member` **->** The member to view the message stats for. Defaults to you.
        """

        if not await ctx.check_channel():
            return

        elif member is not None:
            if member.bot:
                return await ctx.reply(f'{ctx.denial} Bots cannot have message data.')

            data = await self.bot.db.get('stats', member.id)
            if data is None:
                return await ctx.reply(f'{ctx.denial} `{member.display_name}` does not have any message stats.')
        else:
            data = await self.bot.db.get('stats', ctx.author.id)
            if data is None:
                return await ctx.reply(f'{ctx.denial} You do not have any message stats.')

        user = member if member else ctx.author

        m = await ctx.send('Creating charts... Please wait...')
        await self.create_graph(user.id)
        view = utils.SelectChart(ctx, user)
        view.message = m
        await view.start()

    async def inc_stats(self, message):
        if message.guild and not message.author.bot:
            now = datetime.now()
            week_day = now.strftime('%A')  # For the week
            month_day = now.strftime('%d') + ' ' + now.strftime('%B')  # For the month
            month = now.strftime('%B')  # For the year

            # Lose some messages if it means that the heartbeat won't be blocked and
            # that it won't overwrite the reset.
            if not self.bot.resetting_stats:
                server_data: Stats = await self.bot.db.get('stats', 0)
                data: Stats = await self.bot.db.get('stats', message.author.id)
                existed = True
                if data is None:
                    existed = False
                    data: Stats = Stats(
                        id=message.author.id,
                        daily_messages={
                            'reset_when': server_data.daily_messages['reset_when'],
                            'Today': 0
                        },
                        weekly_messages={
                            'reset_when': server_data.weekly_messages['reset_when'],
                            week_day: 0
                        },
                        monthly_messages={
                            'reset_when': server_data.monthly_messages['reset_when'],
                            month_day: 0
                        },
                        yearly_messages={
                            'reset_when': server_data.yearly_messages['reset_when'],
                            month: 0
                        },
                    )

                if data.daily_messages.get('Today') is None:
                    data.daily_messages['Today'] = 1
                else:
                    data.daily_messages['Today'] += 1

                if server_data.daily_messages.get('Today') is None:
                    server_data.daily_messages['Today'] = 1
                else:
                    server_data.daily_messages['Today'] += 1

                if data.weekly_messages.get(week_day) is None:
                    data.weekly_messages[week_day] = 1
                else:
                    data.weekly_messages[week_day] += 1

                if server_data.weekly_messages.get(week_day) is None:
                    server_data.weekly_messages[week_day] = 1
                else:
                    server_data.weekly_messages[week_day] += 1

                if data.monthly_messages.get(month_day) is None:
                    data.monthly_messages[month_day] = 1
                else:
                    data.monthly_messages[month_day] += 1

                if server_data.monthly_messages.get(month_day) is None:
                    server_data.monthly_messages[month_day] = 1
                else:
                    server_data.monthly_messages[month_day] += 1

                if data.yearly_messages.get(month) is None:
                    data.yearly_messages[month] = 1
                else:
                    data.yearly_messages[month] += 1

                if server_data.yearly_messages.get(month) is None:
                    server_data.yearly_messages[month] = 1
                else:
                    server_data.yearly_messages[month] += 1

                if existed is False:
                    await self.bot.db.add('stats', data)
                else:
                    await data.commit()
                await server_data.commit()

    @commands.Cog.listener('on_message')
    async def message_stats_add(self, message: disnake.Message):
        self.bot.loop.create_task(self.inc_stats(message))

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        if member.guild.id != 1097610034701144144:
            return

        await self.bot.db.delete('levels', {'_id': member.id})
        await self.bot.db.delete('stats', {'_id': member.id})


def setup(bot: Astemia):
    bot.add_cog(Levels(bot))
