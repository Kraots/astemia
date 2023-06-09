from __future__ import annotations

import random
import datetime
from asyncio import TimeoutError
from typing import TYPE_CHECKING
from pymongo.errors import DuplicateKeyError

import disnake
from disnake.ui import View, button

import utils

if TYPE_CHECKING:
    from main import Astemia

__all__ = (
    'create_intro',
    'Verify',
)


async def create_intro(webhook: disnake.Webhook, ctx: utils.Context, bot: Astemia, user_id: int = None):
    user_id = user_id or ctx.author.id

    if not isinstance(ctx.channel, disnake.DMChannel):
        if ctx.channel.id not in (
            utils.Channels.bots, utils.Channels.bot_commands, utils.Channels.staff_chat
        ):
            try:
                bot.verifying.pop(bot.verifying.index(user_id))
            except (IndexError, ValueError):
                pass
            return
        else:
            confirm_view = utils.ConfirmView
    else:
        confirm_view = utils.ConfirmViewDMS

    data = await bot.db.get('intro', user_id)
    to_update = False
    if data:
        to_update = True
        view = confirm_view(ctx)
        view.message = await ctx.send(
            'You already have an intro, do you want to edit it?\n'
            '**Note: You can always type `!cancel` or `?cancel` to cancel.**',
            view=view
        )
        await view.wait()
        if view.response is False:
            try:
                bot.verifying.pop(bot.verifying.index(user_id))
            except (IndexError, ValueError):
                pass
            return await view.message.edit(content='Aborted.')

    def check(m):
        if m.content in ('!cancel', '?cancel'):
            bot.verifying.pop(bot.verifying.index(user_id))
            raise utils.Canceled
        return m.channel.id == ctx.channel.id and m.author.id == user_id
    guild = bot.get_guild(1097610034701144144)
    intro_channel = guild.get_channel(utils.Channels.intros)

    try:
        await ctx.reply('What\'s your name?')
    except disnake.HTTPException:
        await ctx.send('What\'s your name?')

    try:
        _name = await bot.wait_for('message', timeout=180.0, check=check)
        name = _name.content
        if len(name) > 100:
            try:
                bot.verifying.pop(bot.verifying.index(user_id))
            except (IndexError, ValueError):
                pass
            return await _name.reply(f'{ctx.denial} Name too long. Type `!intro` to redo.')
        elif len(name) == 0:
            try:
                bot.verifying.pop(bot.verifying.index(user_id))
            except (IndexError, ValueError):
                pass
            return await _name.reply(f'{ctx.denial} You did not say what your name is! Type `!intro` to redo.')

        await _name.reply('What\'s your age?')
        while True:
            try:
                _age = await bot.wait_for('message', timeout=180.0, check=check)
                age = int(_age.content)
            except (ValueError, TypeError):
                await ctx.send(f'{ctx.denial} Must be a number.')
            except TimeoutError:
                try:
                    bot.verifying.pop(bot.verifying.index(user_id))
                except (IndexError, ValueError):
                    pass
                try:
                    return await ctx.reply(f'{ctx.denial} Ran out of time. Type `!intro` to redo.')
                except disnake.Forbidden:
                    return
            else:
                if age < 14 or age > 19:
                    mem = guild.get_member(user_id)
                    if _age.author.id != bot._owner_id:
                        if not any(r for r in utils.StaffRoles.all if r in (role.id for role in mem.roles)):
                            entry: utils.Constants = await bot.db.get('constants')
                            if mem.id not in entry.ogs:
                                if age < 14:
                                    await utils.try_dm(
                                        mem,
                                        f'{ctx.denial} Sorry! You\'re too young for this server.'
                                    )
                                elif age > 19:
                                    await utils.try_dm(
                                        mem,
                                        f'{ctx.denial} Sorry! You\'re too old for this server.'
                                    )
                                try:
                                    bot.verifying.pop(bot.verifying.index(user_id))
                                except (IndexError, ValueError):
                                    pass
                                await mem.ban(reason='User does not match age limits.')
                                await utils.log(
                                    webhook,
                                    title='[BAN]',
                                    fields=[
                                        ('Member', f'{mem} (`{mem.id}`)'),
                                        ('Reason', f'User does not match age requirements. (`{age} y/o`)'),
                                        ('By', f'{bot.user.mention} (`{bot.user.id}`)'),
                                        ('At', utils.format_dt(datetime.datetime.now(), 'F')),
                                    ]
                                )
                                return
                            else:
                                break
                        else:
                            break
                    else:
                        break
                else:
                    break

        await _age.reply(
            'What are your pronouns? '
            '(e.g: he/him, she/her, they/them, he/they, she/they, etc...)\n'
            '***Please be specific!***'
        )
        _pronouns = await bot.wait_for('message', timeout=180.0, check=check)
        pronouns = _pronouns.content
        if len(pronouns) > 100:
            try:
                bot.verifying.pop(bot.verifying.index(user_id))
            except (IndexError, ValueError):
                pass
            return await _pronouns.reply(f'{ctx.denial} Pronouns too long. Type `!intro` to redo.')
        elif len(pronouns) == 0:
            try:
                bot.verifying.pop(bot.verifying.index(user_id))
            except (IndexError, ValueError):
                pass
            return await _pronouns.reply(f'{ctx.denial} You did not say what your pronouns are! Type `!intro` to redo.')

        await _pronouns.reply(
            'What\'s your gender? '
            '(e.g: male, female, non-binary, trans-male, trans-female, etc...)\n'
            '***Please be specific!***'
        )
        _gender = await bot.wait_for('message', timeout=180.0, check=check)
        gender = _gender.content
        if len(gender) > 100:
            try:
                bot.verifying.pop(bot.verifying.index(user_id))
            except (IndexError, ValueError):
                pass
            return await _gender.reply(f'{ctx.denial} Gender too long. Type `!intro` to redo.')
        elif len(gender) == 0:
            try:
                bot.verifying.pop(bot.verifying.index(user_id))
            except (IndexError, ValueError):
                pass
            return await _gender.reply(f'{ctx.denial} You did not say what your gender is! Type `!intro` to redo.')

        await _gender.reply('Where are you from?')
        _location = await bot.wait_for('message', timeout=180.0, check=check)
        location = _location.content
        if len(location) > 100:
            try:
                bot.verifying.pop(bot.verifying.index(user_id))
            except (IndexError, ValueError):
                pass
            return await _location.reply(f'{ctx.denial} Location too long. Type `!intro` to redo.')
        elif len(location) == 0:
            try:
                bot.verifying.pop(bot.verifying.index(user_id))
            except (IndexError, ValueError):
                pass
            return await _location.reply(f'{ctx.denial} You did not say what your location is! Type `!intro` to redo.')

        await _location.reply('Dms? `open` | `closed` | `ask`')
        while True:
            _dms = await bot.wait_for('message', timeout=180.0, check=check)
            dms = _dms.content
            if dms.lower() not in ('open', 'closed', 'ask'):
                await _dms.reply(f'{ctx.denial} Must only be `open` | `closed` | `ask`')
            else:
                break

        await _dms.reply(
            'What\'s your sexuality? '
            '(e.g: straight, bisexual, gay, lesbian, pansexual, etc...)\n'
            '***Please be specific!***'
        )
        _sexuality = await bot.wait_for('message', timeout=180.0, check=check)
        sexuality = _sexuality.content
        if len(sexuality) > 100:
            try:
                bot.verifying.pop(bot.verifying.index(user_id))
            except (IndexError, ValueError):
                pass
            return await ctx.reply(f'{ctx.denial} Sexuality too long. Type `!intro` to redo.')
        elif len(sexuality) == 0:
            try:
                bot.verifying.pop(bot.verifying.index(user_id))
            except (IndexError, ValueError):
                pass
            return await _sexuality.reply(f'{ctx.denial} You did not say what your sexuality is! Type `!intro` to redo.')

        await _sexuality.reply(
            'What do you like?'
            '(e.g: ice-cream, music, gaming, etc.)'
            '\n*Can\'t believe people need an example for this shit.*'
        )
        _likes = await bot.wait_for('message', timeout=180.0, check=check)
        likes = _likes.content
        if len(likes) > 1024:
            try:
                bot.verifying.pop(bot.verifying.index(user_id))
            except (IndexError, ValueError):
                pass
            return await _likes.reply(f'{ctx.denial} You like too many things. Please don\'t go above 1024 '
                                      'characters next time. Type `!intro` to redo.')
        elif len(likes) == 0:
            try:
                bot.verifying.pop(bot.verifying.index(user_id))
            except (IndexError, ValueError):
                pass
            return await _likes.reply(f'{ctx.denial} You did not say what you like! Type `!intro` to redo.')

        await _likes.reply('What do you dislike?')
        _dislikes = await bot.wait_for('message', timeout=180.0, check=check)
        dislikes = _dislikes.content
        if len(dislikes) > 1024:
            try:
                bot.verifying.pop(bot.verifying.index(user_id))
            except (IndexError, ValueError):
                pass
            return await _dislikes.reply(f'{ctx.denial} You dislike too many things. Please don\'t go above 1024 '
                                         'characters next time. Type `!intro` to redo.')
        elif len(dislikes) == 0:
            try:
                bot.verifying.pop(bot.verifying.index(user_id))
            except (IndexError, ValueError):
                pass
            return await _dislikes.reply(f'{ctx.denial} You did not say what you dislike! Type `!intro` to redo.')
    except TimeoutError:
        try:
            bot.verifying.pop(bot.verifying.index(user_id))
        except (IndexError, ValueError):
            pass
        try:
            return await ctx.reply(f'{ctx.denial} Ran out of time. Type `!intro` to redo.')
        except disnake.Forbidden:
            return
    else:
        try:
            bot.verifying.pop(bot.verifying.index(user_id))
        except (IndexError, ValueError):
            pass
        role = guild.get_role(random.choice(utils.all_colour_roles[:-1]))
        usr = guild.get_member(user_id)
        colour = role.color if to_update is False else usr.color
        em = disnake.Embed(colour=colour)
        em.set_author(name=utils.format_name(usr), icon_url=usr.display_avatar)
        em.set_thumbnail(url=usr.display_avatar)
        em.add_field(name='Name', value=name)
        em.add_field(name='Age', value=age)
        em.add_field(name='Pronouns', value=pronouns)
        em.add_field(name='Gender', value=gender)
        em.add_field(name='Location', value=location)
        em.add_field(name='DMs', value=dms)
        em.add_field(name='Sexuality', value=sexuality)
        em.add_field(name='Likes', value=likes)
        em.add_field(name='Dislikes', value=dislikes)
        msg = await intro_channel.send(embed=em)

        if to_update is False:
            new_roles = [r for r in usr.roles if r.id != utils.ExtraRoles.unverified] + [role]
            await usr.edit(roles=new_roles)
            try:
                await bot.db.add('intros', utils.Intro(
                    id=user_id,
                    name=name,
                    age=age,
                    pronouns=pronouns,
                    gender=gender,
                    location=location,
                    dms=dms,
                    sexuality=sexuality,
                    likes=likes,
                    dislikes=dislikes,
                    message_id=msg.id
                ))
            except DuplicateKeyError:
                role = random.choice([r for r in usr.roles if r.id in utils.all_colour_roles])
                new_roles = [r for r in usr.roles if r.id not in utils.all_colour_roles] + [role]
                await usr.edit(roles=new_roles)
                return await utils.try_delete(msg)
        else:
            await utils.try_delete(channel=intro_channel, message_id=data.message_id)

            data.name = name
            data.age = age
            data.pronouns = pronouns
            data.gender = gender
            data.location = location
            data.dms = dms
            data.sexuality = sexuality
            data.likes = likes
            data.dislikes = dislikes
            data.message_id = msg.id
            await data.commit(replace=True)

        await ctx.reply(
            f'Successfully {"edited" if to_update else "created"} your intro. You can see it in {intro_channel.mention}'
        )


class Verify(View):
    def __init__(self, bot: Astemia):
        super().__init__(timeout=None)
        self.bot = bot

    async def on_error(self, error, item, inter):
        await self.bot.inter_reraise(inter, item, error)

    @button(label='Verify', style=disnake.ButtonStyle.green, custom_id='astemia:verify')
    async def verify(self, button: disnake.Button, inter: disnake.MessageInteraction):
        await inter.response.defer()
        disagree = '<:disagree:938412196663271514>'
        if inter.author.id in self.bot.verifying:
            return await inter.followup.send(
                f'> {disagree} Please complete your current verification before proceeding again!', ephemeral=True
            )
        try:
            msg = await inter.author.send('Starting the intro creation process...')
            self.bot.verifying.append(inter.author.id)
        except disnake.Forbidden:
            return await inter.followup.send(f'> {disagree} You have your dms off! Please enable them!!', ephemeral=True)
        ctx = await self.bot.get_context(msg)
        await create_intro(self.bot.webhooks['mod_logs'], ctx, self.bot, inter.author.id)
