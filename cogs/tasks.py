from datetime import datetime
from dateutil.relativedelta import relativedelta

import random

import disnake
from disnake.ext import commands, tasks

import utils
from utils import Poll

from main import Astemia


class Tasks(commands.Cog):
    def __init__(self, bot: Astemia):
        self.bot = bot

        self.servers = [
            1098669760406896813, 1098669783945314364, 1098669730350497823,
            1098668833918697534
        ]

        #  self.send_random_question.start()
        self.check_polls.start()
        self.check_for_stats_reset.start()
        self.notify_bump.start()

    @tasks.loop(hours=3)
    async def send_random_question(self):
        guild = self.bot.get_guild(1097610034701144144)
        channel = guild.get_channel(1078234686528172119)
        entry: utils.Constants = await utils.Constants.get()
        questions = entry.random_questions
        for i in range(9):
            random.shuffle(questions)
        question: str = random.choice(questions)
        await channel.send(question)

    @send_random_question.before_loop
    async def before_rand_q(self):
        await self.bot.wait_until_ready()

    @tasks.loop(seconds=5.0)
    async def check_polls(self):
        polls: list[Poll] = await self.bot.db.find_sorted('polls', 'expire_date', 1)
        for poll in polls:
            if poll.expire_date <= datetime.now():
                channel = self.bot.get_channel(utils.Channels.polls)
                message = await channel.fetch_message(poll.message_id)
                embed = message.embeds[0]
                embed.color = utils.red
                await message.edit(view=None, embed=embed)
                await self.bot.db.delete('polls', {'_id': poll.pk})

    @check_polls.before_loop
    async def before_poll_check(self):
        await self.bot.wait_until_ready()

    @tasks.loop(seconds=60.0)
    async def check_for_stats_reset(self):
        self.bot.resetting_stats = True

        data: utils.Stats = await self.bot.db.get('stats', 0)  # The server collection.
        daily_reset = datetime.fromtimestamp(data.daily_messages['reset_when'])
        weekly_reset = datetime.fromtimestamp(data.weekly_messages['reset_when'])
        monthly_reset = datetime.fromtimestamp(data.monthly_messages['reset_when'])
        yearly_reset = datetime.fromtimestamp(data.yearly_messages['reset_when'])

        guild = self.bot.get_guild(1097610034701144144)

        now = datetime.now()

        if (
            (now >= weekly_reset) or
            (now >= monthly_reset) or
            (now >= yearly_reset)
        ):
            cog = self.bot.get_cog('Levels')
            await cog.create_graph(0)
            weekly_file = disnake.File(
                'stats_chart/server-weekly.png',
                'server-weekly.png'
            )
            monthly_file = disnake.File(
                'stats_chart/server-monthly.png',
                'server-monthly.png'
            )
            yearly_file = disnake.File(
                'stats_chart/server-yearly.png',
                'server-yearly.png'
            )
            channel = guild.get_channel(1097610036026548286)

        if now >= daily_reset:
            new_reset = now + relativedelta(
                days=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )
            for entry in await self.bot.db.find('stats'):
                entry: utils.Stats
                entry.daily_messages = {'reset_when': new_reset.timestamp()}
                await entry.commit()

        if now >= weekly_reset:
            activity = {}

            new_reset = now + relativedelta(
                weeks=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )
            for entry in await self.bot.db.find('stats'):
                entry: utils.Stats

                if entry.id != 0:
                    messages = 0
                    for k, v in entry.weekly_messages.items():
                        if k != 'reset_when':
                            messages += v
                    activity[entry.id] = messages

                entry.weekly_messages = {'reset_when': new_reset.timestamp()}
                await entry.commit()

            top_active = []
            i = 0
            for memid in sorted(activity, key=lambda k: activity[k], reverse=True):
                if activity[memid] != 0:
                    i += 1
                    member = guild.get_member(memid)
                    if member is not None:
                        top_active.append(
                            f'\u2800 `#{i}` {member.display_name} ({activity[memid]:,} messages)\n'
                        )

            total_messages = 0
            for msgs in activity.values():
                total_messages += msgs
            em = disnake.Embed(
                title='Last week\'s activity',
                description='Here\'s the top 5 most active members last week:\n'
                            f'{"".join(top_active[:5])}',
                color=utils.blurple
            )
            em.set_image(f'attachment://{weekly_file.filename}')
            em.set_footer(text=f'Total messages this week: {total_messages:,}')
            await channel.send(embed=em, file=weekly_file)

        if now >= monthly_reset:
            activity = {}

            new_reset = now + relativedelta(
                months=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )
            for entry in await self.bot.db.find('stats'):
                entry: utils.Stats

                if entry.id != 0:
                    messages = 0
                    for k, v in entry.monthly_messages.items():
                        if k != 'reset_when':
                            messages += v
                    activity[entry.id] = messages

                entry.monthly_messages = {'reset_when': new_reset.timestamp()}
                await entry.commit()

            top_active = []
            i = 0
            for memid in sorted(activity, key=lambda k: activity[k], reverse=True):
                if activity[memid] != 0:
                    i += 1
                    member = guild.get_member(memid)
                    if member is not None:
                        top_active.append(
                            f'\u2800 `#{i}` {member.display_name} ({activity[memid]:,} messages)\n'
                        )

            total_messages = 0
            for msgs in activity.values():
                total_messages += msgs
            em = disnake.Embed(
                title='Last month\'s activity',
                description='Here\'s the top 10 most active members last month:\n'
                            f'{"".join(top_active[:10])}',
                color=utils.blurple
            )
            em.set_image(f'attachment://{monthly_file.filename}')
            em.set_footer(text=f'Total messages this month: {total_messages:,}')
            await channel.send(embed=em, file=monthly_file)

        if now >= yearly_reset:
            activity = {}

            new_reset = now + relativedelta(
                years=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )
            for entry in await self.bot.db.find('stats'):
                entry: utils.Stats

                if entry.id != 0:
                    messages = 0
                    for k, v in entry.yearly_messages.items():
                        if k != 'reset_when':
                            messages += v
                    activity[entry.id] = messages

                entry.yearly_messages = {'reset_when': new_reset.timestamp()}
                await entry.commit()

            top_active = []
            i = 0
            for memid in sorted(activity, key=lambda k: activity[k], reverse=True):
                if activity[memid] != 0:
                    i += 1
                    member = guild.get_member(memid)
                    if member is not None:
                        top_active.append(
                            f'\u2800 `#{i}` {member.display_name} ({activity[memid]:,} messages)\n'
                        )

            total_messages = 0
            for msgs in activity.values():
                total_messages += msgs
            em = disnake.Embed(
                title='Last year\'s activity',
                description='Here\'s the top 15 most active members last year:\n'
                            f'{"".join(top_active[:15])}',
                color=utils.blurple
            )
            em.set_image(f'attachment://{yearly_file.filename}')
            em.set_footer(text=f'Total messages this year: {total_messages:,}')
            await channel.send(embed=em, file=yearly_file)

        self.bot.resetting_stats = False

    @check_for_stats_reset.before_loop
    async def wait_for_ready_stats_reset(self):
        await self.bot.wait_until_ready()

    @tasks.loop(seconds=2100.0)
    async def notify_bump(self):
        server = self.servers[0]
        self.servers.append(server)
        self.servers = self.servers[1:]

        guild = self.bot.get_guild(server)
        channel = disnake.utils.find(lambda c: c.name == 'bump', guild.channels)
        if channel:
            await channel.send(
                f'{guild.default_role.mention}\n\n It\'s your turn to bump!\n\n'
                '*If you didn\'t bump within* ***10 minutes*** *from receiving this message, '
                'then wait for the next message '
                'so that you don\'t interfere with the other\'s turns to bump.*',
                allowed_mentions=disnake.AllowedMentions(everyone=True)
            )

    @notify_bump.before_loop
    async def wait_for_ready_bump(self):
        await self.bot.wait_until_ready()


def setup(bot: Astemia):
    bot.add_cog(Tasks(bot))
