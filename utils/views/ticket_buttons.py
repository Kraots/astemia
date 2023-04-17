from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime
from dateutil.relativedelta import relativedelta

import asyncio

import disnake
from disnake.ui import View, Button

import utils
from utils import Ticket
from .confirm_buttons import ConfirmViewInteraction

if TYPE_CHECKING:
    from main import Astemia

__all__ = ('TicketView', 'OpenTicketView')


class TicketView(View):
    def __init__(self, bot: Astemia):
        super().__init__(timeout=None)
        self.bot = bot

    @disnake.ui.button(label='Close', emoji='<:trash:938412197967724554>', custom_id='astemia:tickets')
    async def close(self, button: Button, inter: disnake.MessageInteraction):
        await inter.response.defer()
        ticket: Ticket = await self.bot.db.get('tickets', inter.channel.id)
        em = disnake.Embed(title='Ticket Closed', colour=utils.blurple)
        ticket_owner = inter.guild.get_member(ticket.owner_id)
        if inter.author.id == ticket.owner_id:
            em.description = f'You closed ticket `#{ticket.ticket_id}` ' \
                             f'that you created on {utils.format_dt(ticket.created_at, "F")} ' \
                             f'(`{utils.human_timedelta(ticket.created_at, accuracy=6)}`)'
        else:
            em.description = f'You closed **{ticket_owner.name}**\'s ticket ' \
                             f'that was created on {utils.format_dt(ticket.created_at, "F")} ' \
                             f'(`{utils.human_timedelta(ticket.created_at, accuracy=6)}`)'
            em_2 = disnake.Embed(
                colour=utils.blurple,
                title='Ticket Closed',
                description=f'Your ticket (`#{ticket.ticket_id}`) '
                            f'that you created on {utils.format_dt(ticket.created_at, "F")} '
                            f'(`{utils.human_timedelta(ticket.created_at, accuracy=6)}`)'
                            f'was closed by **{inter.author}**'
            )
            try:
                await ticket_owner.send(embed=em_2)
            except disnake.Forbidden:
                pass
        await utils.try_dm(inter.author, embed=em)
        await inter.channel.delete(reason=f'Ticket Closed by {inter.author} (ID: {inter.author.id})')
        await self.bot.db.delete('tickets', {'_id': ticket.pk})
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[TICKET CLOSED]',
            fields=[
                ('Ticket Owner', f'{ticket_owner} (`{ticket_owner.id}`)'),
                ('Ticket ID', f'`#{ticket.ticket_id}`'),
                ('Closed By', f'{inter.author} (`{inter.author.id}`)'),
                ('At', utils.format_dt(datetime.now(), 'F')),
            ]
        )


class OpenTicketView(View):
    def __init__(self, bot: Astemia):
        super().__init__(timeout=None)
        self.bot = bot

        self.cooldowns = {}

    async def on_error(
        self, error: Exception, item: disnake.ui.Item, interaction: disnake.MessageInteraction
    ) -> None:
        if interaction.response.is_done():
            await interaction.followup.send('An unknown error occurred, sorry', ephemeral=True)
        else:
            await interaction.response.send_message(
                'An unknown error occurred, sorry', ephemeral=True
            )
        await self.ctx.bot.inter_reraise(self.ctx.bot, interaction, item, error)

    def check_cooldown(self, user_id: int) -> bool:
        now = datetime.now()
        if self.cooldowns.get(user_id):
            if now >= self.cooldowns[user_id]:
                self.cooldowns.pop(user_id)
                return True
            else:
                return False
        self.cooldowns[user_id] = now + relativedelta(seconds=30.0)
        return True

    @disnake.ui.button(label='🎟️ Open Ticket', custom_id='astemia:open_ticket', style=disnake.ButtonStyle.blurple)
    async def open_ticket(self, button: Button, inter: disnake.MessageInteraction):
        await asyncio.sleep(.5)
        await inter.response.defer()

        if not self.check_cooldown(inter.author.id):
            return await inter.send(
                'You are on cooldown!',
                ephemeral=True
            )

        view = ConfirmViewInteraction(inter)

        await inter.send(
            'Are you sure you want to open up a ticket?',
            ephemeral=True,
            view=view
        )
        await view.wait()

        if view.response is False:
            return await inter.send(
                '> <:agree:938412298769432586> Cancelled opening the ticket.',
                ephemeral=True
            )
        else:
            await inter.send('> 🎟️ Opening ticket...', ephemeral=True)

        total_tickets: Ticket = await Ticket.find({'owner_id': inter.author.id}).sort('ticket_id', -1).to_list(5)

        if len(total_tickets) >= 5:
            return await inter.send(
                'Cannot create ticket because ticket limit reached (`5`).',
                ephemeral=True
            )
        ticket_id = '1' if not total_tickets else str(int(total_tickets[0].ticket_id) + 1)
        ch_name = f'{inter.author.display_name}-ticket #' + ticket_id

        guild = self.bot.get_guild(1097610034701144144)
        categ = guild.get_channel(utils.Categories.tickets)
        channel = await guild.create_text_channel(
            ch_name,
            category=categ,
            reason=f'Ticket Creation by {utils.format_name(inter.author)} (ID: {inter.author.id})'
        )
        em = disnake.Embed(
            title=f'Ticket #{ticket_id}',
            description='Hello, thanks for creating a ticket. '
                        'Please write out what made you feel like you needed to create a ticket '
                        'and be patient until one of our staff members is available '
                        'to help.'
        )
        m = await channel.send(
            inter.author.mention,
            embed=em,
            view=TicketView(self.bot)
        )

        await self.bot.db.add('tickets', Ticket(
            channel_id=channel.id,
            message_id=m.id,
            owner_id=inter.author.id,
            ticket_id=ticket_id,
            created_at=datetime.utcnow()
        ))

        await m.pin()
        await channel.purge(limit=1)
        await channel.set_permissions(inter.author, read_messages=True)

        v = View()
        v.add_item(Button(label='Jump!', url=m.jump_url))

        staff_chat = guild.get_channel(utils.Channels.staff_chat)
        await staff_chat.send(
            f'@everyone New ticket has been created by `{utils.format_name(inter.author)}`',
            allowed_mentions=disnake.AllowedMentions(everyone=True),
            view=v
        )

        await utils.try_dm(inter.author, 'Ticket created!', view=v)
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[TICKET OPENED]',
            fields=[
                ('Ticket Owner', f'{utils.format_name(inter.author)} (`{inter.author.id}`)'),
                ('Ticket ID', f'`#{ticket_id}`'),
                ('At', utils.format_dt(datetime.now(), 'F')),
            ]
        )
