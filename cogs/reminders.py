import textwrap
import datetime

import disnake
from disnake.ext import commands, tasks

import utils
from utils import (
    human_timedelta,
    UserFriendlyTime,
    Context,
    RoboPages,
    FieldPageSource,
    Reminder
)

from main import Astemia


class Reminders(commands.Cog):
    """Reminder related commands."""

    def __init__(self, bot: Astemia):
        self.bot = bot
        self.check_current_reminders.start()

    @property
    def display_emoji(self) -> str:
        return '⏰'

    @commands.group(invoke_without_command=True, case_insensitive=True, aliases=['reminder'])
    async def remind(
        self,
        ctx: Context,
        *,
        when_and_what: UserFriendlyTime(commands.clean_content, default='...')
    ):
        """Set your reminder.

        `when_and_what` **->** The time to remind you and what to remind you.

        **Example:**
            `!remind 30m sleep`
        """

        res: list[Reminder] = await self.bot.db.find_sorted('reminders', 'reminder_id', 0, {'user_id': ctx.author.id})

        if res:
            new_id = res[0].reminder_id + 1
        else:
            new_id = 1

        await self.bot.db.add('reminders', Reminder(
            reminder_id=new_id,
            user_id=ctx.author.id,
            channel_id=ctx.channel.id,
            remind_when=when_and_what.dt,
            remind_what=when_and_what.arg,
            time_now=datetime.datetime.utcnow(),
            message_url=ctx.message.jump_url
        ))

        delta = human_timedelta(when_and_what.dt, accuracy=3)
        await ctx.send(f'Alright {ctx.author.mention}, in **{delta}**: {when_and_what.arg}')

    @remind.command(name='list')
    async def remind_list(self, ctx: Context):
        """See your list of reminders, if you have any."""

        reminders = []
        entries = await self.bot.db.find_sorted('reminders', 'remind_when', 1, {'user_id': ctx.author.id})
        for entry in entries:
            entry: Reminder

            shorten = textwrap.shorten(entry.remind_what, width=320)
            reminders.append((
                f'(ID) `{entry.reminder_id}`: In {human_timedelta(entry.remind_when)}',
                f'{shorten}\n[Click here to go there]({entry.message_url})'
            ))

        if len(reminders) == 0:
            return await ctx.send('No currently running reminders.')

        src = FieldPageSource(reminders, per_page=5)
        src.embed.title = 'Reminders'
        src.embed.colour = utils.blurple
        pages = RoboPages(src, ctx=ctx, compact=True)
        await pages.start()

    @remind.command(name='remove', aliases=['delete', 'cancel'])
    @commands.max_concurrency(1, commands.BucketType.user)
    async def remind_remove(self, ctx: Context, reminder_id: int):
        """Remove a reminder from your list based on its id.

        `reminder_id` **->** The id of the reminder you want to delete. This can be found by looking at `!remind list`
        """

        entries: list[Reminder] = await self.bot.db.find_one('reminders', {'user_id': ctx.author.id, 'reminder_id': reminder_id})
        if entries:
            entry = entries[0]

            if entry.user_id == ctx.author.id:
                view = utils.ConfirmView(ctx, 'Did not react in time.')
                view.message = msg = await ctx.send(
                    'Are you sure you want to cancel that reminder?',
                    view=view
                )
                await view.wait()
                if view.response is True:
                    await self.bot.db.delete('reminders', {'_id': entry.pk})
                    e = 'Succesfully cancelled the reminder.'
                    return await msg.edit(content=e, view=view)

                elif view.response is False:
                    e = 'Reminder has not been cancelled.'
                    return await msg.edit(content=e, view=view)
            else:
                await ctx.send('That reminder is not yours!')
                return
        else:
            await ctx.send('No reminder with that id.')
            return

    @remind.command(name='clear')
    @commands.max_concurrency(1, commands.BucketType.user)
    async def remind_clear(self, ctx: Context):
        """Delete all of your reminders."""

        res: Reminder = await self.bot.db.find_one('reminders', {'user_id': ctx.author.id})
        if res is not None:
            view = utils.ConfirmView(ctx, 'Did not react in time.')
            view.message = msg = await ctx.reply(
                'Are you sure you want to clear your reminders?',
                view=view
            )
            await view.wait()
            if view.response is True:
                await self.bot.db.delete('reminders', {'user_id': ctx.author.id})
                e = 'Succesfully cleared all your reminders.'
                return await msg.edit(content=e, view=view)

            elif view.response is False:
                e = 'Reminders have not been cleared.'
                return await msg.edit(content=e, view=view)
        else:
            await ctx.send('No currently running reminders.')

    @tasks.loop(seconds=5)
    async def check_current_reminders(self):
        await self.bot.wait_until_ready()
        current_time = datetime.datetime.utcnow()
        entries: list[Reminder] = await self.bot.db.find_sorted('reminders', 'remind_when', 1)
        for entry in entries[:10]:
            if current_time >= entry.remind_when:
                remind_channel = self.bot.get_channel(entry.channel_id)
                msg = f'<@!{entry.user_id}>, **{human_timedelta(entry.time_now)}**: {entry.remind_what}'
                await remind_channel.send(
                    msg,
                    view=utils.UrlButton('Go to the original message', entry.message_url)
                )
                await self.bot.db.delete('reminders', {'_id': entry.pk})

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        if member.guild.id != 1097610034701144144:
            return

        await self.bot.db.delete('reminders', {'user_id': member.id})

    @remind.error
    async def remind_error(self, ctx: Context, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.send(str(error))
        else:
            await ctx.reraise(error)

    @remind_remove.error
    async def remind_remove_error(self, ctx: Context, error):
        if isinstance(error, commands.errors.TooManyArguments):
            return
        else:
            await ctx.reraise(error)


def setup(bot: Astemia):
    bot.add_cog(Reminders(bot))
