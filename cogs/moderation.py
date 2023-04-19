import random
from typing import Literal
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

import disnake
from disnake.ext import commands, tasks

import utils
from utils import (
    Context,
    is_mod,
    is_admin,
    is_owner,
    UserFriendlyTime,
    Mutes,
    format_dt,
    human_timedelta,
    AnnouncementView,
    GiveAway,
    BadWords,
    Channels,
    StaffRoles,
    ExtraRoles,
    Rules,
    Warns
)

from main import Astemia


class Moderation(commands.Cog):
    """Staff related commands."""
    def __init__(self, bot: Astemia):
        self.bot = bot
        self.ignored_channels = (
            Channels.news, Channels.boosts, Channels.rules, Channels.welcome,
            Channels.intros, Channels.roles, Channels.colours, Channels.birthdays,
            Channels.staff_chat, Channels.logs, Channels.messages_logs, Channels.moderation_logs,
            Channels.github, Channels.bot_commands, Channels.verify,
            Channels.recommendations, Channels.polls, Channels.activity_reports,
            Channels.tickets, Channels.discord_news, Channels.discord_safety
        )

        self.check_mutes.start()
        self.check_giveaway.start()
        self.check_streaks.start()
        self.check_warn_streaks.start()

    def jump_view(self, url: str) -> disnake.ui.View:
        view = disnake.ui.View()
        view.add_item(disnake.ui.Button(label='Jump!', url=url))
        return view

    @property
    def display_emoji(self) -> str:
        return '🛠️'

    @commands.command()
    @is_admin()
    async def announce(self, ctx: Context):
        """Make an announcement in <#1078234682963021846>"""

        view = AnnouncementView(self.bot, ctx.author)
        view.message = await ctx.send(embed=view.prepare_embed(), view=view)

    @commands.command(name='purge', aliases=('clear',))
    @is_mod()
    async def chat_purge(self, ctx: Context, amount: int):
        """Clear the ``amount`` of messages from the chat.

        `amount` **->** The amount of messages to delete from the current channel.
        """

        await utils.try_delete(ctx.message)
        purged = await ctx.channel.purge(limit=amount)
        msg = await ctx.send(f'> {ctx.agree} Deleted `{len(purged):,}` messages')
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[CHAT PURGE]',
            fields=[
                ('Channel', ctx.channel.mention),
                ('Amount', f'`{utils.plural(len(purged)):message}`'),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ],
            view=self.jump_view(ctx.message.jump_url)
        )
        await utils.try_delete(msg, delay=5.0)

    @commands.group(name='lock', invoke_without_command=True, case_insensitive=True)
    @is_mod()
    async def lock_channel(self, ctx: Context, channel: disnake.TextChannel = None):
        """
        Locks the channel.
        No one will be able to talk in that channel except the mods, but everyone will still see the channel.

        `channel` **->** The channel to lock. If you want to lock the current channel you use the command, you can ignore this since it defaults to the current channel.
        """  # noqa

        channel = channel or ctx.channel

        role = channel.guild.default_role
        if channel.id not in self.ignored_channels:
            overwrites = channel.overwrites_for(role)
            overwrites.send_messages = False
            await channel.set_permissions(
                role,
                overwrite=overwrites,
                reason=f'Channel locked by {utils.format_name(ctx.author)} ({ctx.author.id})'
            )
        else:
            return await ctx.reply(f'{ctx.denial} That channel cannot be locked.')
        await ctx.reply('> 🔒 Channel Locked!')
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[CHANNEL LOCK]',
            fields=[
                ('Channel', channel.mention),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ],
            view=self.jump_view(ctx.message.jump_url)
        )

    @lock_channel.command(name='all')
    @is_mod()
    async def lock_all_channels(self, ctx: Context):
        """
        Locks *all* the channels that are have not been locked, but omits the channels that the users can't see or talk in already.
        """

        _channels = []
        role = ctx.guild.default_role
        for channel in ctx.guild.text_channels:
            if channel.id not in self.ignored_channels:
                if channel.overwrites_for(role).send_messages is not False:
                    overwrites = channel.overwrites_for(role)
                    overwrites.send_messages = False
                    await channel.set_permissions(
                        role,
                        overwrite=overwrites,
                        reason=f'Channel locked by {utils.format_name(ctx.author)} ({ctx.author.id})'
                    )
                    _channels.append(channel.mention)
        await ctx.reply('> 🔒 All the unlocked channels have been locked!')
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[CHANNEL LOCK]',
            fields=[
                ('Channel', ' '.join(_channels)),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ],
            view=self.jump_view(ctx.message.jump_url)
        )

    @commands.group(name='unlock', invoke_without_command=True, case_insensitive=True)
    @is_mod()
    async def unlock_channel(self, ctx: Context, channel: disnake.TextChannel = None):
        """
        Unlocks the channel.

        `channel` **->** The channel to unlock. If you want to unlock the current channel you use the command, you can ignore this since it defaults to the current channel.
        """  # noqa

        channel = channel or ctx.channel

        role = channel.guild.default_role
        if channel.id not in self.ignored_channels:
            overwrites = channel.overwrites_for(role)
            overwrites.send_messages = None
            await channel.set_permissions(
                role,
                overwrite=overwrites,
                reason=f'Channel unlocked by {utils.format_name(ctx.author)} ({ctx.author.id})'
            )
        else:
            return await ctx.reply(f'{ctx.denial} That channel cannot be unlocked.')
        await ctx.reply('> 🔓 Channel Unlocked!')
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[CHANNEL UNLOCK]',
            fields=[
                ('Channel', channel.mention),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ],
            view=self.jump_view(ctx.message.jump_url)
        )

    @unlock_channel.command(name='all')
    @is_mod()
    async def unlock_all_channels(self, ctx: Context):
        """
        Unlocks *all the already locked* channels, but omits the channels that the users can't see or talk in already.
        """

        _channels = []
        role = ctx.guild.default_role
        for channel in ctx.guild.text_channels:
            if channel.id not in self.ignored_channels:
                if channel.overwrites_for(role).send_messages is not None:
                    overwrites = channel.overwrites_for(role)
                    overwrites.send_messages = None
                    await channel.set_permissions(
                        role,
                        overwrite=overwrites,
                        reason=f'Channel unlocked by {utils.format_name(ctx.author)} ({ctx.author.id})'
                    )
                    _channels.append(channel.mention)
        await ctx.reply('> 🔓 All locked channels have been unlocked!')
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[CHANNEL UNLOCK]',
            fields=[
                ('Channel', ' '.join(_channels)),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ],
            view=self.jump_view(ctx.message.jump_url)
        )

    @commands.command(name='ban')
    @is_admin()
    async def _ban(self, ctx: Context, member: disnake.Member | disnake.User, *, reason: str):
        """Bans an user.

        `member` **->** The member to ban. If the member is not in the server you must provide their discord id.
        `reason` **->** The reason you're banning the member.
        """

        if isinstance(member, disnake.Member):
            if await ctx.check_perms(member) is False:
                return

        await utils.try_dm(
            member,
            f'> ⚠️ Hello! Sadly, you have been **banned** from `Astemia` for **{reason}**. Goodbye 👋'
        )

        await ctx.astemia.ban(
            member,
            reason=f'{utils.format_name(ctx.author)} ({ctx.author.id}): "{reason}"',
            delete_message_days=0
        )
        await self.bot.db.delete('mutes', {'_id': member.id})
        await ctx.send(f'> 👌 🔨 Banned `{member}` for **{reason}**')
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[BAN]',
            fields=[
                ('Member', f'{member} (`{member.id}`)'),
                ('Reason', reason),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ],
            view=self.jump_view(ctx.message.jump_url)
        )

    @_ban.error
    async def _ban_error(self, ctx: Context, error):
        if isinstance(error, commands.BadUnionArgument):
            return await ctx.reply(f'{ctx.denial} Could not find member.')
        await ctx.reraise(error)

    @commands.command(name='unban')
    @is_admin()
    async def _unban(self, ctx: Context, *, user: disnake.User):
        """Unbans an user.

        `user` **->** The user to unban. Must be their discord id.
        """

        try:
            await ctx.astemia.unban(user, reason=f'Unban by {utils.format_name(ctx.author)} ({ctx.author.id})')
        except disnake.NotFound:
            return await ctx.reply(f'{ctx.denial} The user is not banned.')

        else:
            await ctx.reply(f'> 👌 Successfully unbanned `{user}`')
            await utils.log(
                self.bot.webhooks['mod_logs'],
                title='[UNBAN]',
                fields=[
                    ('Member', f'{user.mention} (`{user.id}`)'),
                    ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                    ('At', format_dt(datetime.now(), 'F')),
                ],
                view=self.jump_view(ctx.message.jump_url)
            )

    @commands.command(name='kick')
    @is_mod()
    async def _kick(self, ctx: Context, member: disnake.Member, *, reason: str):
        """Kicks a member.

        `member` **->** The member to kick.
        `reason` **->** The reason you're kicking the member.
        """

        if await ctx.check_perms(member) is False:
            return

        await utils.try_dm(
            member,
            f'> ⚠️ Hello! Sadly, you have been **kicked** from `Astemia` for **{reason}**. Goodbye 👋'
        )
        await member.kick(reason=f'{utils.format_name(ctx.author)} ({ctx.author.id}): "{reason}"')
        await ctx.send(f'> 👌 Kicked `{member}` for **{reason}**')
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[KICK]',
            fields=[
                ('Member', f'{member} (`{member.id}`)'),
                ('Reason', reason),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ],
            view=self.jump_view(ctx.message.jump_url)
        )

    async def apply_mute_or_block(
        self,
        action: Literal['mute', 'block'],
        ctx: Context,
        member: disnake.Member,
        *,
        _time_and_reason: str
    ):
        if await ctx.check_perms(member) is False:
            return

        fmt = 'muted' if action == 'mute' else 'blocked'
        kwargs = {}
        if action == 'mute':
            kwargs['muted'] = True
        else:
            kwargs['blocked'] = True

        usr: Mutes = await self.bot.db.get('mutes', member.id)
        _ctx = ctx
        if usr is not None and usr.is_muted is True:
            muted_by = ctx.astemia.get_member(usr.muted_by)
            data = await UserFriendlyTime(commands.clean_content).convert(ctx, _time_and_reason)
            if usr.blocked is True and action == 'block':
                if usr.filter is False:
                    if ctx.author.id not in (usr.muted_by, self.bot._owner_id):
                        if usr.muted_by == self.bot._owner_id:
                            return await ctx.reply(
                                f'{member.mention} was **{fmt}** by `{muted_by}` which is in a '
                                'higher role hierarcy than you. Only staff members of the same '
                                f'role or above can edit the **{action}** time and reason that person.'
                            )

                view = utils.ConfirmView(ctx)
                view.message = await ctx.reply(
                    'That user is already blocked. Do you wish to renew their '
                    f'block to `{human_timedelta(data.dt, suffix=False)}` and '
                    f'with the new reason being **{utils.remove_markdown(data.arg)}**?',
                    view=view
                )
                await view.wait()
                if view.response is False:
                    return await view.message.edit(
                        content=f'Successfully aborted editing the block time and reason for {member.mention}'
                    )
                await self.apply_unmute_or_unblock(
                    action='unblock',
                    ctx=ctx,
                    member=member,
                    send_feedback=False
                )
                msg = await ctx.send('Preparing to edit the block...')
                _ctx = await self.bot.get_context(msg)
                await utils.try_delete(msg)
            elif usr.muted is True and action == 'mute':
                if usr.filter is False:
                    if ctx.author.id not in (usr.muted_by, self.bot._owner_id):
                        if usr.muted_by == self.bot._owner_id:
                            return await ctx.reply(
                                f'{member.mention} was **{fmt}** by `{muted_by}` which is in a '
                                'higher role hierarcy than you. Only staff members of the same '
                                f'role or above can edit the **{action}** time and reason that person.'
                            )

                view = utils.ConfirmView(ctx)
                view.message = await ctx.reply(
                    'That user is already muted. Do you wish to renew their '
                    f'mute to `{human_timedelta(data.dt, suffix=False)}` and '
                    f'with the new reason being **{utils.remove_markdown(data.arg)}**?',
                    view=view
                )
                await view.wait()
                if view.response is False:
                    return await view.message.edit(
                        content=f'Successfully aborted editing the mute time and reason for {member.mention}'
                    )
                await self.apply_unmute_or_unblock(
                    action='unmute',
                    ctx=ctx,
                    member=member,
                    send_feedback=False
                )
                msg = await ctx.send('Preparing to edit the mute...')
                _ctx = await self.bot.get_context(msg)
                await utils.try_delete(msg)
            else:
                if usr.filter is False:
                    if ctx.author.id not in (usr.muted_by, self.bot._owner_id):
                        if usr.muted_by == self.bot._owner_id:
                            _ = 'muted' if usr.muted is True else 'blocked'
                            return await ctx.reply(
                                f'{member.mention} was **{fmt}** by `{muted_by}` which is in a '
                                'higher role hierarcy than you. Only staff members of the same '
                                f'role or above can edit the **{action}** time and reason that person.'
                            )
                _action = 'unblock' if action == 'mute' else 'unmute'
                await self.apply_unmute_or_unblock(
                    action=_action,
                    ctx=ctx,
                    member=member,
                    send_feedback=False
                )
                msg = await ctx.send(
                    f'Preparing to edit from {"mute" if action == "block" else "block"} to {action}...'
                )
                _ctx = await self.bot.get_context(msg)
                await utils.try_delete(msg)

        time_and_reason = await UserFriendlyTime(commands.clean_content).convert(_ctx, _time_and_reason)
        time = time_and_reason.dt
        reason = time_and_reason.arg
        duration = human_timedelta(time, suffix=False)
        data: Mutes = await self.bot.db.get('mutes', member.id)
        existed = True
        if data is None:
            existed = False
            data = Mutes(
                id=member.id,
                muted_by=ctx.author.id,
                muted_until=time,
                reason=reason,
                duration=duration,
                filter=False,
                is_muted=True,
                **kwargs,
            )
        else:
            data.muted_by = ctx.author.id
            data.muted_until = time
            data.reason = reason
            data.duration = duration
            data.filter = False
            data.is_muted = True
            if kwargs.get('muted') is True:
                data.muted = True
            elif kwargs.get('blocked') is True:
                data.blocked = True

        if StaffRoles.owner in (r.id for r in member.roles):  # Checks for owner
            data.is_owner = True
        elif StaffRoles.admin in (r.id for r in member.roles):  # Checks for admin
            data.is_admin = True
        elif StaffRoles.moderator in (r.id for r in member.roles):  # Checks for mod
            data.is_mod = True

        role = ctx.astemia.get_role(ExtraRoles.muted) if action == 'mute' else ctx.astemia.get_role(ExtraRoles.blocked)
        new_roles = [role for role in member.roles
                     if role.id not in (StaffRoles.all)
                     ] + [role]
        await member.edit(
            roles=new_roles,
            voice_channel=None,
            reason=f'[{action.upper()}] {utils.format_name(ctx.author)} ({ctx.author.id}): "{reason}"'
        )

        em = disnake.Embed(title=f'You have been {fmt}!', color=utils.red)
        em.description = f'**{fmt.title()} By:** {utils.format_name(ctx.author)}\n' \
                         f'**Reason:** {reason}\n' \
                         f'**{action.title()} Duration:** `{human_timedelta(time, suffix=False)}`\n' \
                         f'**Expire Date:** {format_dt(time, "F")}'
        em.set_footer(text=f'{fmt.title()} in `Astemia`')
        em.timestamp = datetime.now(timezone.utc)
        await utils.try_dm(member, embed=em)

        _msg = await ctx.reply(
            f'> 👌 📨 Applied **{action}** to {member.mention} '
            f'until {format_dt(time, "F")} (`{human_timedelta(time, suffix=False)}`)'
        )
        data.jump_url = _msg.jump_url
        if existed is False:
            await self.bot.db.add('mutes', data)
        else:
            await data.commit()
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title=f'[{action.upper()}]',
            fields=[
                ('Member', f'{utils.format_name(member)} (`{member.id}`)'),
                ('Reason', reason),
                (f'{action.title()} Duration', f'`{duration}`'),
                ('Expires At', format_dt(time, "F")),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ],
            view=self.jump_view(_msg.jump_url)
        )

    async def apply_unmute_or_unblock(
        self,
        action: Literal['unmute', 'unblock'],
        ctx: Context,
        *,
        member: disnake.Member | disnake.User,
        send_feedback: bool = True
    ):
        data: Mutes = await self.bot.db.get('mutes', member.id)
        fmt = 'muted' if action == 'unmute' else 'blocked'
        if data is None:
            return await ctx.reply(f'`{utils.format_name(member)}` is not **{fmt}**!')

        if isinstance(member, disnake.User):
            await self.bot.db.delete('mutes', {'_id': data.pk})
            return await ctx.reply(
                'Since that user is not in the server, '
                'his data has been deleted from the muted/blocked database.'
            )

        muted_by = ctx.astemia.get_member(data.muted_by)
        if data.filter is False:
            if ctx.author.id not in (data.muted_by, self.bot._owner_id):
                if data.muted_by == self.bot._owner_id or ctx.author.top_role < muted_by.top_role:
                    return await ctx.reply(
                        f'{member.mention} was **{fmt}** by `{muted_by}` which is in a higher role hierarcy than you. '
                        f'Only staff members of the same role or above can **{action}** that person.'
                    )

        # Since there's now 'streaks' I can't just delete their data.
        # Instead, there's gonna be another task to check every 10 seconds
        # for streak removals.
        if data.filter is True:
            if data.streak == 7:
                await self.bot.db.delete('mutes', {'_id': data.pk})
            else:
                data.streak_expire_date = datetime.now() + relativedelta(days=21)
                data.is_muted = False
                await data.commit()
        else:
            if data.streak == 0:
                await self.bot.db.delete('mutes', {'_id': data.pk})
            else:
                data.is_muted = False
                await data.commit()

        new_roles = [role for role in member.roles if role.id not in (ExtraRoles.muted, ExtraRoles.blocked)]
        if data.is_owner is True:
            owner_role = ctx.astemia.get_role(StaffRoles.owner)  # Check for owner
            new_roles += [owner_role]
        elif data.is_admin is True:
            admin_role = ctx.astemia.get_role(StaffRoles.admin)  # Check for admin
            new_roles += [admin_role]
        elif data.is_mod is True:
            mod_role = ctx.astemia.get_role(StaffRoles.moderator)  # Check for mod
            new_roles += [mod_role]
        await member.edit(roles=new_roles, reason=f'[{action.upper()}] {action.title()} by {utils.format_name(ctx.author)} ({ctx.author.id})')
        if send_feedback is True:
            await utils.try_dm(
                member,
                f'Hello, you have been **un{fmt}** in `Astemia` by **{utils.format_name(ctx.author)}**'
            )

            await ctx.reply(f'> 👌 Successfully **un{fmt}** {member.mention}')

        if data.permanent is True:
            duration = 'PERMANENT'
            remaining = 'PERMANENT'
        else:
            duration = data.duration
            remaining = human_timedelta(data.muted_until, suffix=False, accuracy=6)

        await utils.log(
            self.bot.webhooks['mod_logs'],
            title=f'[{action.upper()}]',
            fields=[
                ('Member', f'{utils.format_name(member)} (`{member.id}`)'),
                (f'{"Mute" if action == "unmute" else "Block"} Duration', f'`{duration}`'),
                ('Remaining', f'`{remaining}`'),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ],
            view=self.jump_view(ctx.message.jump_url)
        )

    @commands.command(name='mute')
    @is_mod()
    async def mute_cmd(
        self,
        ctx: Context,
        member: disnake.Member,
        *,
        time_and_reason: str
    ):
        """
        Mute somebody.

        `member` **->** The member you want to mute.
        `time_and_reason` **->** The time and the reason why you're muting the member.

        **Example:**
        `!mute @carrot 2m coolest person alive`
        `!mute @carrot 1 Jan coolest person alive` (will mute them until 1 January, next year, or this one, depending whether this date has passed. You can also directly specify the year.)
        """  # noqa

        await self.apply_mute_or_block(
            action='mute',
            ctx=ctx,
            member=member,
            _time_and_reason=time_and_reason
        )

    @commands.command(name='unmute')
    @is_mod()
    async def unmute_cmd(self, ctx: Context, *, member: disnake.Member):
        """Unmute somebody that is currently muted.

        `member` **->** The member you want to unmute. If the member was muted by carrot then you can't do shit about it <:lipbite:1097656674912829460> <:kek:1097656660241166356>
        """  # noqa

        await self.apply_unmute_or_unblock(
            action='unmute',
            ctx=ctx,
            member=member
        )

    @commands.command(name='block')
    @is_mod()
    async def block_cmd(
        self,
        ctx: Context,
        member: disnake.Member,
        *,
        time_and_reason: str
    ):
        """
        Block somebody from seeing all of the channels.

        `member` **->** The member you want to block.
        `time_and_reason` **->** The time and the reason why you're blocking the member.

        **Example:**
        `!block @carrot 2m coolest person alive`
        `!block @carrot 1 Jan coolest person alive` (will block them until 1 January, next year, or this one, depending whether this date has passed. You can also directly specify the year.)
        """  # noqa

        await self.apply_mute_or_block(
            action='block',
            ctx=ctx,
            member=member,
            _time_and_reason=time_and_reason
        )

    @commands.command(name='unblock')
    @is_mod()
    async def unblock_cmd(self, ctx: Context, *, member: disnake.Member):
        """Unblock somebody that is currently blocked.

        `member` **->** The member you want to unblock. If the member was blocked by carrot then you can't do shit about it <:lipbite:1097656674912829460> <:kek:1097656660241166356>
        """  # noqa

        await self.apply_unmute_or_unblock(
            action='unblock',
            ctx=ctx,
            member=member
        )

    @mute_cmd.error
    @block_cmd.error
    async def mute_or_block_cmd_error(self, ctx: Context, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.reply(f'{ctx.denial} {error}')
        await ctx.reraise(error)

    @tasks.loop(seconds=15.0)
    async def check_mutes(self):
        mutes: list[Mutes] = await self.bot.db.find_sorted('mutes', 'muted_until', 1, {'is_muted': True})
        for mute in mutes[:15]:
            if datetime.now(mute.muted_until.tzinfo) >= mute.muted_until:
                guild = self.bot.get_guild(1097610034701144144)
                member = guild.get_member(mute.id)
                _mem = f'**[LEFT]** (`{mute.id}`)'
                if mute.blocked is True:
                    action = 'block'
                    fmt = 'unblocked'
                elif mute.muted is True:
                    action = 'mute'
                    fmt = 'unmuted'

                if member:
                    _mem = f'{utils.format_name(member)} (`{member.id}`)'
                    new_roles = [role for role in member.roles if role.id not in (ExtraRoles.blocked, ExtraRoles.muted)]
                    if mute.is_owner is True:
                        owner_role = guild.get_role(StaffRoles.owner)  # Check for owner
                        new_roles += [owner_role]
                    elif mute.is_admin is True:
                        admin_role = guild.get_role(StaffRoles.admin)  # Check for admin
                        new_roles += [admin_role]
                    elif mute.is_mod is True:
                        mod_role = guild.get_role(StaffRoles.moderator)  # Check for mod
                        new_roles += [mod_role]
                    await member.edit(roles=new_roles, reason=f'[{fmt.upper()}] {action.title()} Expired.')
                    await utils.try_dm(
                        member,
                        f'Hello, your **{action}** in `Astemia` has expired. You have been **{fmt}**.'
                    )

                if mute.filter is True:
                    mute.is_muted = False
                    mute.streak_expire_date = datetime.now() + relativedelta(days=21)
                    await mute.commit()
                else:
                    if mute.streak == 0:
                        await self.bot.db.delete('mutes', {'_id': mute.id})
                    else:
                        mute.is_muted = False
                        await mute.commit()

                mem = guild.get_member(mute.muted_by)
                await utils.log(
                    self.bot.webhooks['mod_logs'],
                    title=f'[{action.upper()} EXPIRED]',
                    fields=[
                        ('Member', _mem),
                        ('Reason', mute.reason),
                        (f'{action.title()} Duration', f'`{mute.duration}`'),
                        ('By', mem.mention),
                        ('At', format_dt(datetime.now(), 'F')),
                    ],
                    view=self.jump_view(mute.jump_url)
                )

    @check_mutes.before_loop
    async def mutes_wait_until_ready(self):
        await self.bot.wait_until_ready()

    @tasks.loop(seconds=15.0)
    async def check_streaks(self):
        mutes: list[Mutes] = await self.bot.db.find_sorted('mutes', 'streak_expire_date', 1, {'is_muted': False})
        for mute in mutes[:10]:
            if datetime.now() >= mute.streak_expire_date:
                await self.bot.db.delete('mutes', {'_id': mute.pk})

                guild = self.bot.get_guild(1097610034701144144)
                usr = guild.get_member(mute.id)
                if usr:
                    mem = f'{utils.format_name(usr)} (`{usr.id}`)'
                else:
                    mem = f'**[LEFT]** (`{mute.id}`)'

                await utils.log(
                    self.bot.webhooks['mod_logs'],
                    title='[STREAK RESET]',
                    fields=[
                        ('User', mem),
                        ('At', format_dt(datetime.now(), 'F')),
                    ]
                )

    @check_streaks.before_loop
    async def streaks_wait_until_ready(self):
        await self.bot.wait_until_ready()

    @commands.group(
        name='make',
        invoke_without_command=True,
        case_insensitive=True,
        ignore_extra=False,
        hidden=True
    )
    @is_admin()
    async def staff_make(self, ctx: Context):
        """Shows the help for the `!make` command, used to add more staff members."""

        await ctx.send_help('make')

    @staff_make.command(name='owner')
    @commands.is_owner()
    async def staff_make_owner(self, ctx: Context, *, member: disnake.Member):
        """Make somebody an owner.

        `member` **->** The member you want to make an owner.
        """

        if await ctx.check_perms(member) is False:
            return

        if StaffRoles.owner in (r.id for r in member.roles):
            return await ctx.reply(f'{ctx.denial} `{utils.format_name(member)}` is already an owner!')
        owner_role = ctx.astemia.get_role(StaffRoles.owner)
        await member.edit(roles=[
            r for r in member.roles if r.id not in (StaffRoles.admin, StaffRoles.moderator)
        ] + [owner_role])
        await ctx.reply(f'> 👌 Successfully made `{utils.format_name(member)}` an owner.')
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[OWNER ADDED]',
            fields=[
                ('Member', f'{utils.format_name(member)} (`{member.id}`)'),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ],
            view=self.jump_view(ctx.message.jump_url)
        )

    @staff_make.command(name='admin')
    @is_owner()
    async def staff_make_admin(self, ctx: Context, *, member: disnake.Member):
        """Make somebody an admin.

        `member` **->** The member you want to make an admin.
        """

        if await ctx.check_perms(member) is False:
            return

        if StaffRoles.admin in (r.id for r in member.roles):
            return await ctx.reply(f'{ctx.denial} `{utils.format_name(member)}` is already an admin!')
        admin_role = ctx.astemia.get_role(StaffRoles.admin)
        await member.edit(roles=[
            r for r in member.roles if r.id not in (StaffRoles.owner, StaffRoles.moderator)
        ] + [admin_role])
        await ctx.reply(f'> 👌 Successfully made `{utils.format_name(member)}` an admin.')
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[ADMIN ADDED]',
            fields=[
                ('Member', f'{utils.format_name(member)} (`{member.id}`)'),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ],
            view=self.jump_view(ctx.message.jump_url)
        )

    @staff_make.command(name='moderator', aliases=('mod',))
    @is_admin()
    async def staff_make_mod(self, ctx: Context, *, member: disnake.Member):
        """Make somebody a moderator.

        `member` **->** The member you want to make a moderator.
        """

        if await ctx.check_perms(member) is False:
            return

        if StaffRoles.moderator in (r.id for r in member.roles):
            return await ctx.reply(f'{ctx.denial} `{utils.format_name(member)}` is already a moderator!')
        mod_role = ctx.astemia.get_role(StaffRoles.moderator)
        await member.edit(roles=[
            r for r in member.roles if r.id not in (StaffRoles.owner, StaffRoles.admin)
        ] + [mod_role])
        await ctx.reply(f'> 👌 Successfully made `{utils.format_name(member)}` a moderator.')
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[MODERATOR ADDED]',
            fields=[
                ('Member', f'{utils.format_name(member)} (`{member.id}`)'),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ],
            view=self.jump_view(ctx.message.jump_url)
        )

    @commands.group(
        name='remove',
        invoke_without_command=True,
        case_insensitive=True,
        ignore_extra=False,
        hidden=True
    )
    @is_admin()
    async def staff_remove(self, ctx: Context):
        """Shows the help for the `!remove` command, used to remove a staff member from their position."""

        await ctx.send_help('remove')

    @staff_remove.group(
        name='owner',
        invoke_without_command=True,
        case_insensitive=True,
        ignore_extra=False
    )
    @commands.is_owner()
    async def staff_remove_owner(self, ctx: Context, *, member: disnake.Member):
        """Remove an owner.

        `member` **->** The member you want to remove owner from.
        """

        if await ctx.check_perms(member) is False:
            return

        if StaffRoles.owner not in (r.id for r in member.roles):
            return await ctx.reply(f'{ctx.denial} `{utils.format_name(member)}` is not an owner!')
        await member.edit(roles=[r for r in member.roles if r.id != StaffRoles.owner])
        await ctx.reply(f'> 👌 Successfully removed `{utils.format_name(member)}` from being an owner.')
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[OWNER REMOVED]',
            fields=[
                ('Member', f'{utils.format_name(member)} (`{member.id}`)'),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ],
            view=self.jump_view(ctx.message.jump_url)
        )

    @staff_remove_owner.command(name='all')
    @is_owner(owner_only=True)
    async def remove_owner_all(self, ctx: Context):
        """Remove the owner role from everybody that has it."""

        owners = []
        role = ctx.astemia.get_role(StaffRoles.owner)
        for member in role.members:
            await member.edit(roles=[r for r in member.roles if not r.id == StaffRoles.owner])
            owners.append(member)

        await ctx.reply(f'Successfully removed `{len(owners):,}` owners.')
        formatted = '\n'.join([f'{utils.format_name(member)} (`{member.id}`)' for member in owners])
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[OWNER(S) REMOVED]',
            fields=[
                ('Member(s)', formatted),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ],
            view=self.jump_view(ctx.message.jump_url)
        )

    @staff_remove.group(
        name='admin',
        invoke_without_command=True,
        case_insensitive=True,
        ignore_extra=False
    )
    @is_owner()
    async def staff_remove_admin(self, ctx: Context, *, member: disnake.Member):
        """Remove an admin.

        `member` **->** The member you want to remove admin from.
        """

        if await ctx.check_perms(member) is False:
            return

        if StaffRoles.admin not in (r.id for r in member.roles):
            return await ctx.reply(f'{ctx.denial} `{utils.format_name(member)}` is not an admin!')
        await member.edit(roles=[r for r in member.roles if r.id != StaffRoles.admin])
        await ctx.reply(f'> 👌 Successfully removed `{utils.format_name(member)}` from being an admin.')
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[ADMIN REMOVED]',
            fields=[
                ('Member', f'{utils.format_name(member)} (`{member.id}`)'),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ],
            view=self.jump_view(ctx.message.jump_url)
        )

    @staff_remove_admin.command(name='all')
    @is_owner(owner_only=True)
    async def remove_admin_all(self, ctx: Context):
        """Remove the admin role from everybody that has it."""

        admins = []
        role = ctx.astemia.get_role(StaffRoles.admin)
        for member in role.members:
            await member.edit(roles=[r for r in member.roles if not r.id == StaffRoles.admin])
            admins.append(member)

        await ctx.reply(f'Successfully removed `{len(admins):,}` admins.')
        formatted = '\n'.join([f'{utils.format_name(member)} (`{member.id}`)' for member in admins])
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[ADMIN(S) REMOVED]',
            fields=[
                ('Member(s)', formatted),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ],
            view=self.jump_view(ctx.message.jump_url)
        )

    @staff_remove.group(
        name='moderator',
        aliases=('mod',),
        invoke_without_command=True,
        case_insensitive=True,
        ignore_extra=False
    )
    @is_admin()
    async def staff_remove_mod(self, ctx: Context, *, member: disnake.Member):
        """Remove a moderator.

        `member` **->** The member you want to remove the moderator from.
        """

        if await ctx.check_perms(member) is False:
            return

        if StaffRoles.moderator not in (r.id for r in member.roles):
            return await ctx.reply(f'{ctx.denial} `{utils.format_name(member)}` is not a moderator!')
        await member.edit(roles=[r for r in member.roles if r.id != StaffRoles.moderator])
        await ctx.reply(f'> 👌 Successfully removed `{utils.format_name(member)}` from being a moderator.')
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[MODERATOR REMOVED]',
            fields=[
                ('Member', f'{utils.format_name(member)} (`{member.id}`)'),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ],
            view=self.jump_view(ctx.message.jump_url)
        )

    @staff_remove_mod.command(name='all')
    @is_owner(owner_only=True)
    async def remove_mod_all(self, ctx: Context):
        """Remove the moderator role from everybody that has it."""

        moderators = []
        role = ctx.astemia.get_role(StaffRoles.moderator)
        for member in role.members:
            await member.edit(roles=[r for r in member.roles if not r.id == StaffRoles.moderator])
            moderators.append(member)

        await ctx.reply(f'Successfully removed `{len(moderators):,}` moderators.')
        formatted = '\n'.join([f'{utils.format_name(member)} (`{member.id}`)' for member in moderators])
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[MODERATOR(S) REMOVED]',
            fields=[
                ('Member(s)', formatted),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ],
            view=self.jump_view(ctx.message.jump_url)
        )

    async def end_giveaway(self, gw: GiveAway):
        guild = self.bot.get_guild(1097610034701144144)
        participants = gw.participants + [0]
        random.shuffle(participants)
        while True:
            winner_id = random.choice(participants)
            winner = guild.get_member(winner_id)
            if winner is None:
                participants.pop(participants.index(winner_id))
                if len(participants) == 0:
                    winner = 'No One.'
                    break
            else:
                winner = f'{winner.mention} (`{winner.id}`)'
                break

        channel = guild.get_channel(gw.channel_id)

        try:
            msg = await channel.fetch_message(gw.id)
        except disnake.NotFound:
            return await self.bot.db.delete('giveaways', {'_id': gw.pk})

        em = msg.embeds[0]
        em.color = utils.red
        em.title = '🎁 Giveaway Ended'
        em.add_field('Winner', winner, inline=False)

        v = disnake.ui.View()
        btn = disnake.ui.ActionRow.rows_from_message(msg)[0].children[0]
        btn.disabled = True
        v.add_item(btn)
        await msg.edit(embed=em, view=v)
        await msg.unpin(reason='Giveaway Ended.')

        fmt = '**⚠️ Giveaway Ended ⚠️**'
        if winner != 'No One.':
            fmt += f'\nCongratulations {winner}, you won **{gw.prize}**'
        else:
            fmt += '\nIt appears that no one that participated was still in the server. No winner.'
        await msg.reply(fmt)
        await self.bot.db.delete('giveaways', {'_id': gw.pk})

    @commands.group(
        name='giveaway',
        aliases=('gw',),
        invoke_without_command=True,
        case_insensitive=True,
        hidden=True
    )
    @is_admin()
    async def base_giveaway(self, ctx: Context):
        """The base command for all the giveaway commands."""

        await ctx.send_help('gw')

    @base_giveaway.command(name='create')
    @is_admin()
    async def giveaway_create(self, ctx: Context):
        """Create a giveaway. The giveaway message is sent and pinned in <#1097610035548393514>"""

        view = utils.GiveAwayCreationView(self.bot, ctx.author)
        view.message = await ctx.send(embed=view.prepare_embed(), view=view)

    @base_giveaway.command(name='cancel', aliases=('end',))
    @is_admin()
    async def giveaway_cancel(self, ctx: Context, *, giveaway_id: int):
        """Cancel a giveaway.

        `giveaway_id` **->** The id of the message of the giveaway.
        """

        gw = await self.bot.db.get('giveaways', giveaway_id)
        if gw is None:
            return await ctx.reply('Giveaway with that message id not found.')

        await self.end_giveaway(gw)
        await ctx.reply('Giveaway successfully ended.')

    @base_giveaway.command(name='participants', aliases=('members',))
    @is_mod()
    async def giveaway_participants(self, ctx: Context, *, giveaway_id: int):
        """Look at the participants of a specific giveaway.

        `giveaway_id` **->** The id of the message of the giveaway.
        """

        data: GiveAway = await self.bot.db.get('giveaways', giveaway_id)
        if data is None:
            return await ctx.reply('Giveaway with that message id not found.')

        entries = []
        for mem_id in data.participants:
            mem = ctx.astemia.get_member(mem_id)
            if mem is None:
                mem = f'**[LEFT]** (`{mem_id}`)'
            entries.append(mem)

        paginator = utils.SimplePages(ctx, entries=entries, compact=True)
        paginator.embed.title = 'Here are the participants of this giveaway'
        await paginator.start(ref=True)

    @commands.Cog.listener()
    async def on_ready(self):
        for gw in await self.bot.db.find('giveaways'):
            gw: GiveAway
            view = disnake.ui.View(timeout=None)
            view.add_item(utils.JoinGiveawayButton(str(len(gw.participants))))
            self.bot.add_view(view, message_id=gw.id)

    @tasks.loop(seconds=30.0)
    async def check_giveaway(self):
        giveaways: list[GiveAway] = await self.bot.db.find_sorted('giveaways', 'expire_date', 1)
        now = datetime.now()
        for gw in giveaways[:10]:
            if gw.expire_date <= now:
                await self.end_giveaway(gw)

    @check_giveaway.before_loop
    async def wait_until_ready_(self):
        await self.bot.wait_until_ready()

    @commands.group(
        name='badwords', aliases=('badword', 'words', 'word', 'bad'),
        invoke_without_command=True, case_insensitive=True
    )
    @is_mod()
    async def base_bad_words(self, ctx: Context):
        """See a list of all the currently added bad words."""

        data: BadWords = await self.bot.db.get('badwords')
        if data is None or not data.bad_words:
            return await ctx.reply(f'{ctx.denial} There are no currently added bad words.')

        sorted_ = [w for w in sorted(data.bad_words.keys())]
        entries = []
        for word in sorted_:
            added_by_id = data.bad_words[word]
            added_by = ctx.astemia.get_member(added_by_id)
            added_by = f'**{added_by.display_name}#{added_by.tag}**' or '**[LEFT]**'
            added_by = added_by + f' (`{added_by_id}`)'

            entries.append(
                f'`{word}` - added by {added_by}'
            )

        pag = utils.SimplePages(ctx, entries, compact=True)
        pag.embed.title = 'Here\'s all the currently added bad words'
        await pag.start(ref=True)

    @base_bad_words.command(name='add')
    @is_admin()
    async def add_bad_word(self, ctx: Context, *, word: str):
        """Adds a bad word to the existing bad words.

        `word` **->** The word you want to add.
        """

        word = word.lower()
        data: BadWords = await self.bot.db.get('badwords')
        existed = True
        if data is None:
            existed = False
            data = BadWords()

        if word in [w for w in data.bad_words.keys()]:
            return await ctx.reply(f'{ctx.denial} That bad word is already added in the list.')

        self.bot.bad_words[word] = ctx.author.id
        data.bad_words[word] = ctx.author.id
        if existed is False:
            await self.bot.db.add('badwords', data)
        else:
            await data.commit()

        await ctx.reply(f'Successfully **added** `{word}` to the bad words list.')

    @base_bad_words.command(name='remove')
    @is_admin()
    async def remove_bad_word(self, ctx: Context, *, word: str):
        """Removes a bad word to the existing bad words.

        `word` **->** The word you want to remove.
        """

        word = word.lower()
        data: BadWords = await self.bot.db.get('badwords')
        if data is None or not data.bad_words:
            return await ctx.reply(f'{ctx.denial} There are no currently added bad words.')
        elif word not in data.bad_words.keys():
            return await ctx.reply(f'{ctx.denial} That word is not added in list of bad words.')

        del data.bad_words[word]
        del self.bot.bad_words[word]
        await data.commit()

        await ctx.reply(f'Successfully **removed** `{word}` to the bad words list.')

    @base_bad_words.command(name='clear')
    @is_owner()
    async def clear_bad_word(self, ctx: Context):
        """Clear the custom bad words. This deletes all of them."""

        data: BadWords = await self.bot.db.get('badwords')
        if data is None or not data.bad_words:
            return await ctx.reply(f'{ctx.denial} There are no currently added bad words.')

        data.bad_words = {}
        self.bot.bad_words = {}
        await data.commit()

        await ctx.reply('Successfully **cleared** the bad words list.')

    @commands.group(
        name='questions',
        aliases=('question', 'randomquestion', 'randquestion'),
        invoke_without_command=True,
        case_insensitive=True
    )
    @is_mod()
    async def base_random_question(self, ctx: Context):
        """Shows all the currently added questions."""

        entry: utils.Constants = await self.bot.db.get('constants')
        if len(entry.random_questions) == 0:
            return await ctx.reply('There are no currently added questions.')

        questions = []
        for i, question in enumerate(entry.random_questions):
            questions.append(f'`{i + 1}.` {question}')

        pag = utils.RawSimplePages(ctx, questions, compact=True)
        pag.embed.title = 'Here\'s all the currently added questions:'

        await pag.start()

    @base_random_question.command(name='add')
    @is_mod()
    async def rand_q_add(self, ctx: Context, *, question: str):
        """Adds a random question.

        `question` **->** The question to add.
        """

        question = question[0].upper() + question[1:]  # Make sure that the first letter is always uppercase.
        entry: utils.Constants = await self.bot.db.get('constants')
        entry.random_questions.append(question)
        await entry.commit()

        await ctx.reply(f'> {ctx.agree} Succesfully added the question.')

    @base_random_question.command(name='remove', aliases=('delete',))
    @is_mod()
    async def rand_q_remove(self, ctx: Context, index: str):
        """Removes a random question.

        `question` **->** The question to remove.
        """

        index = utils.format_amount(index)
        try:
            index = int(index) - 1
        except ValueError:
            return await ctx.reply('The index must be a number.')

        if index <= -1:
            return await ctx.reply('The index cannot be 0 or lower.')
        entry: utils.Constants = await self.bot.db.get('constants')
        if (index + 1) > len(entry.random_questions):
            return await ctx.reply('No question found at the given index.')

        entry.random_questions.pop(index)
        await entry.commit()

        await ctx.reply(f'> {ctx.agree} Successfully removed the question.')

    @base_random_question.command(name='clear')
    @is_owner(owner_only=True)
    async def rand_q_clear(self, ctx: Context):
        """Clears all questions."""

        entry: utils.Constants = await self.bot.db.get('constants')
        if len(entry.random_questions) == 0:
            return await ctx.reply('There are no currently added question to clear.')

        view = utils.ConfirmView(ctx)
        view.message = await ctx.reply(
            'Are you sure you want to clear the questions?',
            view=view
        )
        await view.wait()
        if view.response is False:
            return await view.message.edit(
                content='The questions have not been cleared.'
            )

        entry.random_questions = []
        await entry.commit()

        await ctx.reply(
            'Successfully cleared the random questions. '
            'There are now no random questions added anymore.'
        )

    @commands.group(
        name='staffrules', invoke_without_command=True, case_insensitive=True, aliases=('staffrule',)
    )
    @is_mod()
    async def staff_rules(self, ctx: Context, *, rule: int = None):
        """Sends the staff rules. If ``rule`` is given, it will only send that rule.

        `rule` **->** The number of the rule you wish to see. (can be found by counting the rules yourself)
        """

        rules: Rules = await self.bot.db.get('rules', 0)  # In here only the staff rules are stored.
        if rules is None:
            return await ctx.reply(f'{ctx.denial} There are currently no staff rules set. Please contact the owner about this!')
        em = disnake.Embed(title='Staff Rules', color=utils.red)

        if rule is None:
            for rule in rules.rules:
                if em.description is None:
                    em.description = f'• {rule}'
                else:
                    em.description += f'\n\n• {rule}'
        else:
            if rule <= 0:
                return await ctx.reply(f'{ctx.denial} Rule cannot be equal or less than `0`')
            try:
                _rule = rules.rules[rule - 1]
                em.description = f'• {_rule}'
            except IndexError:
                return await ctx.reply(f'{ctx.denial} Rule does not exist!')

        em.set_footer(
            text='NOTE: Not abiding these rules will start with warns and eventually loss '
                 'of the staff role, be it moderator or admin.'
        )

        await ctx.better_reply(embed=em)

    @staff_rules.command(name='add')
    @utils.is_owner()
    async def staff_rules_add(self, ctx: Context, *, rule: str):
        """Adds a rule to the staff's rules.

        `rule` **->** The rule to add.
        """

        rules: Rules = await self.bot.db.get('rules', 0)
        if rules is None:
            await self.bot.db.add('rules', Rules(
                id=0,
                rules=[rule]
            ))
        else:
            rules.rules += [rule]
            await rules.commit()

        await ctx.reply(f'> 👌 📝 `{rule}` successfully **added** to the staff rules.')

    @staff_rules.command(name='edit')
    @utils.is_owner()
    async def staff_rules_edit(self, ctx: Context, rule: int, *, new_rule: str):
        """Edits an existing rule.

        `rule` **->** The number of the rule to edit. (can be found by counting the rules yourself)
        `new_rule` **->** The new rule to replace it with.
        """

        rules: Rules = await self.bot.db.get('rules', 0)
        if rules is None:
            return await ctx.reply(f'{ctx.denial} There are currently no rules set.')
        elif rule == 0:
            return await ctx.reply('Rule cannot be ``0``')

        rule -= 1
        try:
            rules.rules[rule] = new_rule
        except IndexError:
            return await ctx.reply('Rule does not exist!')
        await rules.commit()

        await ctx.reply(f'> 👌 📝 Successfully **edited** rule `{rule + 1}` to `{new_rule}`.')

    @staff_rules.command(name='delete')
    @utils.is_owner()
    async def staff_rules_remove(self, ctx: Context, rule: int):
        """Removes a rule from the staff's rules by its number.

        `rule` **->** The number of the rule to remove. (can be found by counting the number of rules yourself)
        """

        rules: Rules = await self.bot.db.get('rules', 0)
        if rules is None:
            return await ctx.reply(f'{ctx.denial} There are currently no rules set.')
        else:
            if rule <= 0:
                return await ctx.reply(f'{ctx.denial} Rule cannot be equal or less than `0`')
            try:
                rules.rules.pop(rule - 1)
            except IndexError:
                return await ctx.reply(f'{ctx.denial} Rule does not exist!')
            await rules.commit()

        await ctx.reply(f'> 👌 Successfully **removed** rule `{rule}`.')

    @staff_rules.command(name='clear')
    @utils.is_owner()
    async def staff_rules_clear(self, ctx: Context):
        """Deletes all the staff rules."""

        rules: Rules = await self.bot.db.get('rules', 0)
        if rules is None:
            return await ctx.reply(f'{ctx.denial} There are currently no rules set.')
        else:
            await self.bot.db.delete('rules', {'_id': 0})

        await ctx.reply('> 👌 Successfully **cleared** the rules.')

    @commands.group(
        name='ogs', invoke_without_command=True, case_insensitive=True, aliases=('og',)
    )
    @is_mod()
    async def base_ogs(self, ctx: Context):
        """Shows the ogs."""

        entry: utils.Constants = await self.bot.db.get('constants')
        if len(entry.ogs) == 0:
            return await ctx.reply(f'{ctx.denial} There are no added ogs.')

        ogs = []
        guild = self.bot.get_guild(1097610034701144144)
        if guild is not None:
            for user_id in entry.ogs:
                member = guild.get_member(user_id)
                if member is None:
                    member = await self.bot.fetch_user(user_id)

                ogs.append(f'{member} (`{member.id}`)')

        else:
            for user_id in entry.ogs:
                member = await self.bot.fetch_user(user_id)
                ogs.append(f'{member} (`{member.id}`)')

        paginator = utils.SimplePages(ctx, ogs, per_page=10, compact=True, entries_name='users')
        paginator.embed.title = 'Here\'s the og users'
        paginator.embed.color = None
        await paginator.start()

    @base_ogs.command(name='add')
    @is_mod()
    async def add_ogs(self, ctx: Context, members: commands.Greedy[disnake.Member]):
        """This command is used to add people that are very active and thet we'd
        like to save the tag of in case the server gets terminated. This will
        save their ids in the database, and when retrieved the bot will return
        their correct user no matter if they change their username or even the tag.

        `members` **->** The members to add.
        """

        if len(members) == 0:
            return await ctx.reply(f'{ctx.denial} You have to specify what members to add.')

        added_ogs = []
        entry: utils.Constants = await self.bot.db.get('constants')
        for member in members:
            if member.id not in entry.ogs:
                added_ogs.append(f'`{member.display_name}`')
                entry.ogs.append(member.id)

        if len(added_ogs) == 0:
            return await ctx.reply(f'{ctx.denial} Those members have already been added.')

        await entry.commit()
        await ctx.reply(f'Successfully added {" | ".join(added_ogs)}')

    @base_ogs.command(name='remove')
    @is_admin()
    async def remove_og(self, ctx: Context, user_ids: commands.Greedy[int]):
        """Removes the specified ogs based on their user ids.

        `user_ids` **->** The ids of the og users to remove.
        """

        if len(user_ids) == 0:
            return await ctx.reply(f'{ctx.denial} You have not specified any ids of the ogs to remove.')

        entry: utils.Constants = await self.bot.db.get('constants')
        if len(entry.ogs) == 0:
            return await ctx.reply(f'{ctx.denial} There are no added ogs.')

        failed_removal = []
        success_removal = []
        for user_id in user_ids:
            try:
                entry.ogs.remove(user_id)
            except ValueError:
                failed_removal.append(str(user_id))
            else:
                success_removal.append(str(user_id))

        em = disnake.Embed(title='Removed the following ogs', color=utils.red)
        em.add_field(
            name='Successful removals',
            value='\n'.join(success_removal) if len(success_removal) != 0 else 'none',
            inline=False
        )
        em.add_field(
            name='Failed removals',
            value='\n'.join(failed_removal) if len(failed_removal) != 0 else 'none',
            inline=False
        )

        if len(success_removal) != 0:
            await entry.commit()

        await ctx.reply(embed=em)

    def get_mute_time(self, streak: int) -> str:
        if streak == 1:
            return '2 hours'
        elif streak == 2:
            return '5 hours'
        elif streak == 3:
            return '10 hours'
        elif streak == 4:
            return '1 days'
        elif streak == 5:
            return '14 days'
        elif streak == 6:
            return '1 month'
        else:
            return 'permanent'  # This shouldn't really even happen, but just in case it really gets that bad.

    @commands.group(
        name='warn', invoke_without_command=True, case_insensitive=True, aliases=('warns',)
    )
    @is_mod()
    @commands.max_concurrency(1, commands.BucketType.member)
    async def warn_base(self, ctx: Context, members: commands.Greedy[disnake.Member]):
        """Warn a member or multiple at once.

        `members` **->** Either one or multiple members that you wish to warn for breaking the rules.
        """

        await ctx.trigger_typing()

        if len(members) == 0:
            return await ctx.reply(f'{ctx.denial} You must mention the members or give in their ids.')

        reset_warns = datetime.now() + relativedelta(days=3)
        reset_streak = datetime.now() + relativedelta(days=21)

        normal_members_warned = 0
        for member in members:
            if member.id == self.bot._owner_id:
                continue
            elif ctx.author.top_role <= member.top_role:
                continue

            normal_members_warned += 1

            entry: Warns = await self.bot.db.get('warns', member.id)
            if entry is None:
                await self.bot.db.add('warns', Warns(
                    id=member.id,
                    warned_by={str(ctx.author.id): 1},
                    warn_count=1,
                    mute_streak=0,
                    reset_warns=reset_warns,
                    reset_streak=reset_streak
                ))
                entry: Warns = await self.bot.db.get('warns', member.id)
            else:
                usr = entry.warned_by.get(str(ctx.author.id))
                if usr is not None:
                    entry.warned_by[str(ctx.author.id)] += 1
                else:
                    entry.warned_by[str(ctx.author.id)] = 1

                entry.warn_count += 1
                entry.reset_warns = reset_warns

            await ctx.reply(f'> {ctx.agree} {member.mention} has been warned. (`{entry.warn_count}/3`)')

            if entry.warn_count >= 3:
                entry.warn_count = 0
                entry.reset_streak = entry.reset_streak
                entry.mute_streak += 1

                _duration = self.get_mute_time(entry.mute_streak)
                kwargs = {'permanent': False}
                time_and_reason = await UserFriendlyTime(commands.clean_content).convert(
                    ctx,
                    f'{_duration if _duration != "permanent" else "999 years"} 3 Warns Reached'
                )

                if _duration == 'permanent':
                    kwargs['permanent'] = True

                time = time_and_reason.dt
                duration = human_timedelta(time, suffix=False)
                reason = time_and_reason.arg
                data: Mutes = await self.bot.db.get('mutes', member.id)
                existed = True
                if data is None:
                    existed = False
                    data: Mutes = Mutes(
                        id=member.id,
                        muted_by=self.bot.user.id,
                        muted_until=time,
                        reason=reason,
                        duration=duration,
                        filter=False,
                        is_muted=True,
                        muted=True,
                        **kwargs
                    )
                else:
                    data.muted_by = self.bot.user.id
                    data.muted_until = time
                    data.reason = reason
                    data.duration = duration
                    data.filter = False
                    data.is_muted = True
                    data.muted = True
                    if kwargs['permanent'] is True:
                        data.permanent = True

                if StaffRoles.owner in (r.id for r in member.roles):  # Checks for owner
                    data.is_owner = True
                elif StaffRoles.admin in (r.id for r in member.roles):  # Checks for admin
                    data.is_admin = True
                elif StaffRoles.moderator in (r.id for r in member.roles):  # Checks for mod
                    data.is_mod = True

                role = ctx.astemia.get_role(ExtraRoles.muted)
                new_roles = [role for role in member.roles
                             if role.id not in (StaffRoles.all)
                             ] + [role]
                await member.edit(
                    roles=new_roles,
                    voice_channel=None,
                    reason=f'[Mute] {utils.format_name(self.bot.user)} ({self.bot.user.id}): "{reason}"'
                )

                if data.permanent:
                    mute_duration = 'PERMANENT'
                    expires_at = 'PERMANENT'
                else:
                    mute_duration = _duration
                    expires_at = format_dt(time, "F")

                em = disnake.Embed(title='You have been muted!', color=utils.red)
                em.description = f'**Muted By:** {utils.format_name(self.bot.user)}\n' \
                                 f'**Reason:** {reason}\n' \
                                 f'**Mute Duration:** `{mute_duration}`\n' \
                                 f'**Expire Date:** {expires_at}'
                em.set_footer(text='Muted in `Astemia`')
                em.timestamp = datetime.now(timezone.utc)
                await utils.try_dm(member, embed=em)

                _msg = await ctx.send(
                    f'> ⚠️ **[AUTOMOD: {reason.upper()}]** {member.mention} has been **muted** for '
                    f'**{reason.lower()}** '
                    f'until {expires_at} (`{mute_duration}`)'
                )

                data.jump_url = _msg.jump_url
                if existed is False:
                    await self.bot.db.add('mutes', data)
                else:
                    await data.commit()
                await utils.log(
                    self.bot.webhooks['mod_logs'],
                    title='[MUTE]',
                    fields=[
                        ('Member', f'{utils.format_name(member)} (`{member.id}`)'),
                        ('Reason', reason),
                        ('Mute Duration', f'`{mute_duration}`'),
                        ('Expires At', expires_at),
                        ('By', f'{self.bot.user.mention} (`{self.bot.user.id}`)'),
                        ('At', format_dt(datetime.now(), 'F')),
                    ],
                    view=self.jump_view(_msg.jump_url)
                )

            await entry.commit()

        if normal_members_warned == 0:
            await ctx.reply(
                f'{ctx.denial} No one has been warned because they are '
                'higher or equal than you on the hierarchy.'
            )

    @warn_base.command(name='remove')
    @is_admin()
    async def remove_warn(self, ctx: Context, member: disnake.Member):
        """Remove ONE warn from the member.

        `member` **->** The member to remove a warn from.
        """

        entry: Warns = await self.bot.db.get('warns', member.id)
        if entry is None:
            return await ctx.reply(f'{ctx.denial} The user has no warns.')
        elif entry.warn_count == 0:
            return await ctx.reply(f'{ctx.denial} The user is currently at **0** active warns.')

        entry.warn_count -= 1
        await entry.commit()

        await ctx.reply(f'> {ctx.agree} Successfully removed 1 active warn from {member.mention}')

    @warn_base.command(name='show')
    @is_mod()
    async def warn_show(self, ctx: Context, member: disnake.Member):
        """Show the warn for the specific member you want.

        `member` **->** The member to show the amount of warns of.
        """

        entry: Warns = await self.bot.db.get('warns', member.id)
        if entry is None:
            return await ctx.reply(f'{ctx.denial} The member has no warns active.')

        _warns_by = []
        total_warns = 0
        for warns in entry.warned_by.values():
            total_warns += warns

        for k in sorted(entry.warned_by, reverse=True, key=lambda k: entry.warned_by[k]):
            mem = ctx.astemia.get_member(int(k))
            warn_count = entry.warned_by[k]
            _warns_by.append(
                f'\u2800\u2800• {utils.format_name(mem)} - {warn_count} warns'
            )

        warns_by = '\n'.join(_warns_by)
        em = disnake.Embed(title=f'Warns for {member.display_name}', color=utils.red)
        em.description = f'**{entry.warn_count}** Active Warns.\n\n**{total_warns}** Total Warns.' \
                         f'\nWarns by:\n{warns_by}'

        await ctx.reply(embed=em)

    @tasks.loop(seconds=1800.0)
    async def check_warn_streaks(self):
        now = datetime.now()
        warns_reset: list[Warns] = await self.bot.db.find_sorted('warns', 'reset_warns', 1)
        streak_reset: list[Warns] = await self.bot.db.find_sorted('warns', 'reset_streak', 1)

        for warn in warns_reset[:30]:
            if now >= warn.reset_warns:
                warn.reset_warns = now + relativedelta(years=999)
                warn.warn_count = 0
                await warn.commit()

                if warn.mute_streak == 0:
                    await self.bot.db.delete('warns', {'_id': warn.pk})

        for warn in streak_reset[:30]:
            if now >= warn.reset_streak:
                warn.reset_streak = now + relativedelta(years=999)
                warn.mute_streak = 0
                await warn.commit()

                if warn.warn_count == 0:
                    await self.bot.db.delete('warns', {'_id': warn.pk})

    @check_warn_streaks.before_loop
    async def warn_before_loop(self):
        await self.bot.wait_until_ready()

    @commands.command(name='selfie', aliases=('selfies',))
    @is_mod()
    async def selfies(self, ctx: Context, member: disnake.Member, *, extra_message: str = None):
        """A command that automatically sends the message telling the member that they have broken the seflie channel rule.

        `member` **->** The member that broke the rule.
        `extra_message` **->** Anything extra you want to add at the end of the normal warn text.
        """

        reference = ctx.message.reference.resolved if ctx.message.reference else None

        message = f"{member.mention} Your selfie/message has been deleted because it " \
                  "violates the rules of this channel. Please check the topic of the " \
                  "channel next time."

        if extra_message is not None:
            extra_message = extra_message.strip()
            extra_message = extra_message.split()
            extra_message[0] = extra_message[0].title()
            extra_message = ' '.join(extra_message)
            if not extra_message.endswith('.') or not extra_message.endswith('!'):
                extra_message = extra_message + '.'

            message = message + f'\n*Note from staff: {extra_message}*'

        if reference:
            await reference.delete()

        await ctx.send(message)


def setup(bot: Astemia):
    bot.add_cog(Moderation(bot))
