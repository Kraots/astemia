import os

from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

import disnake
from disnake.ext import commands, tasks

import utils

from main import Astemia


class Welcome(commands.Cog):
    def __init__(self, bot: Astemia):
        self.bot = bot
        self.files = {}
        self.send_welc.start()

    @tasks.loop(seconds=15.0)
    async def send_welc(self):
        if self.files:
            webhook = self.bot.webhooks.get('welcome_webhook')
            if webhook is not None:
                if len(self.files) == 10:
                    await webhook.send(files=self.files.values())
                else:
                    files = []
                    count = 0
                    for file in self.files.values():
                        count += 1
                        files.append(file)
                        if count == 10:
                            await webhook.send(files=files)
                            count = 0
                            files = []
                    if len(files) != 0:
                        await webhook.send(files=files)
                        files = []
                self.files = {}

                # We delete all the png files in the folder
                # so that they don't stack up a lot and end up
                # using a ton of space when they're useless to be
                # kept.
                os.system('rm welcomes/*')

    @commands.Cog.listener('on_member_join')
    async def on_member_join(self, member: disnake.Member):
        entry: utils.Constants = await self.bot.db.get('constants')
        days_ago = datetime.now(timezone.utc) - relativedelta(days=entry.min_account_age)
        if member.created_at > days_ago:
            await utils.try_dm(member, 'Your account is too new to be allowed in the server.')
            await member.ban(reason='Account too new.')
            return await utils.log(
                self.bot.webhooks['mod_logs'],
                title='[BAN]',
                fields=[
                    ('Member', f'{utils.format_name(member)} (`{member.id}`)'),
                    ('Reason', 'Account too new.'),
                    ('Account Created', utils.human_timedelta(member.created_at, accuracy=7)),
                    ('By', f'{self.bot.user.mention} (`{self.bot.user.id}`)'),
                    ('At', utils.format_dt(datetime.now(), 'F')),
                ]
            )

        if member.guild.id != 1097610034701144144:  # Only continue if it's actual astemia server.
            return

        extra_guild = self.bot.get_guild(1098669760406896813)
        extra_guild_2 = self.bot.get_guild(1098669783945314364)
        extra_guild_3 = self.bot.get_guild(1098669730350497823)
        extra_guild_4 = self.bot.get_guild(1098668833918697534)
        if member in extra_guild.members:
            await extra_guild.ban(member, reason='Joined Main Server')
        elif member in extra_guild_2.members:
            await extra_guild_2.ban(member, reason='Joined Main Server')
        elif member in extra_guild_3.members:
            await extra_guild_3.ban(member, reason='Joined Main Server')
        elif member in extra_guild_4.members:
            await extra_guild_4.ban(member, reason='Joined Main Server')

        guild = self.bot.get_guild(1097610034701144144)
        if member.bot:
            bot_role = guild.get_role(utils.ExtraRoles.bot)
            await member.add_roles(bot_role, reason='Bot Account.')
            return

        await utils.check_username(self.bot, member=member, bad_words=self.bot.bad_words.keys())
        unverified_role = guild.get_role(utils.ExtraRoles.unverified)
        await member.add_roles(unverified_role)

        member_count = len([m for m in guild.members if not m.bot])
        file = await utils.create_welcome_card(member, member_count)
        self.files[member.id] = file

        mute: utils.Mutes = await self.bot.db.get('mute', member.id)
        if mute is not None and mute.is_muted is True:
            if mute.blocked is True:
                action = 'block'
                fmt = 'blocked'
            elif mute.muted is True:
                action = 'mute'
                fmt = 'muted'

            if mute.permanent is True:
                expire_date = 'PERMANENT'
                remaining = 'PERMANENT'
            else:
                expire_date = utils.format_dt(mute.muted_until, "F")
                remaining = utils.human_timedelta(mute.muted_until, suffix=False, accuracy=6)

            role = guild.get_role(utils.ExtraRoles.muted) if action == 'mute' else guild.get_role(utils.ExtraRoles.blocked)
            mem = guild.get_member(mute.muted_by)
            await member.add_roles(role, reason=f'[{action.title()} EVASION] user joined but was still {fmt} in the database')
            em = disnake.Embed(title=f'You have been {fmt}!', color=utils.red)
            em.description = f'**{fmt.title()} By:** {self.bot.user}\n' \
                             f'**Originally {fmt.title()} By:** {mem.mention}' \
                             f'**Reason:** {action.title} Evasion.\n' \
                             f'**Expire Date:** {expire_date}\n' \
                             f'**Remaining:** `{remaining}`'
            em.set_footer(text=f'{fmt.title()} in `Astemia`')
            em.timestamp = datetime.now(timezone.utc)
            await utils.try_dm(member, embed=em)

            view = disnake.ui.View()
            view.add_item(disnake.ui.Button(label='Jump!', url=mute.jump_url))
            await utils.log(
                self.bot.webhooks['mod_logs'],
                title=f'[{action.upper()} EVASION]',
                fields=[
                    ('Member', f'{utils.format_name(member)} (`{member.id}`)'),
                    ('Reason', f'{action.title()} Evasion.'),
                    ('Expires At', expire_date),
                    ('Remaining', f'`{remaining}`'),
                    ('By', f'{self.bot.user.mention} (`{self.bot.user.id}`)'),
                    ('Originally By', f'{mem.mention} (`{mem.id}`)'),
                    ('At', utils.format_dt(datetime.now(), 'F')),
                ],
                view=view
            )

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        if member.guild.id != 1097610034701144144:
            return

        if member.id in self.files:
            del self.files[member.id]


def setup(bot: Astemia):
    bot.add_cog(Welcome(bot))
