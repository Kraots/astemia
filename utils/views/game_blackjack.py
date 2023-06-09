from __future__ import annotations
from typing import TYPE_CHECKING

import random

import disnake
from disnake import MessageInteraction, ButtonStyle
from disnake.ui import View, button, Button

import utils
from utils import Game

if TYPE_CHECKING:
    from main import Astemia

__all__ = ('BlackJack',)

hyperlink = '[`{0}`](https://cdn.discordapp.com/attachments/938411306762002456/938443265252925510/rickroll.gif "{0}")'


class Player:
    def __init__(self, is_dealer=False) -> None:
        self.cards = []
        self.card_value = 0
        self.is_dealer = is_dealer

    def calculate_card_value(self) -> int:
        value = 0
        a_count = 0
        for card in self.cards:
            if card.name == 'A':
                a_count += 1
            elif card.name in ('K', 'Q', 'J'):
                value += 10
            else:
                value += int(card.name)

        if not self.is_dealer:
            if a_count != 0:
                for _ in range(a_count):
                    if value + 11 > 21:
                        value += 1
                    else:
                        value += 11
            self.card_value = value
            return value
        else:
            if a_count != 0:
                for _ in range(a_count):
                    if value > 17:
                        value += 1
                    else:
                        value += 11
            self.card_value = value
            return value


class Card:
    def __init__(self, suit: str, name: str):
        self.suit = suit
        self.name = name

    def __str__(self):
        return hyperlink.format(f'{self.suit} {self.name}')


class Deck:
    suits = ('♣️', '♥️', '♦️', '♠️')
    cards_set = ('A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'K', 'Q', 'J')

    def __init__(self):
        self.cards = self.build_deck()
        self.shuffle()

    def build_deck(self) -> list[Card]:
        return [Card(suit, card) for suit in self.suits for card in self.cards_set]

    def shuffle(self) -> None:
        for _ in range(random.randint(1, 9)):
            random.shuffle(self.cards)

    def get_random_cards(self, count: int) -> list[Card]:
        cards_list = []
        for i in range(count):
            random_card = random.choice(self.cards)
            cards_list.append(random_card)
            self.cards.remove(random_card)
        return cards_list

    def get_random_card(self) -> Card:
        return self.get_random_cards(1)[0]

    def give_random_card(self, player: Player, count: int) -> None:
        for random_card in self.get_random_cards(count):
            player.cards.append(random_card)
        player.calculate_card_value()


class BlackJack(View):
    message: disnake.Message

    def __init__(
        self,
        user: disnake.Member,
        bot: Astemia,
        bet_amount: int
    ):
        super().__init__(timeout=15.0)
        self.user = user
        self.bot = bot
        self.bet_amount = bet_amount

        self.build_table()

    def build_table(self):
        while True:
            self.deck = Deck()
            self.player = Player()
            self.dealer = Player(is_dealer=True)
            self.deck.give_random_card(self.player, 2)
            self.deck.give_random_card(self.dealer, 2)

            if self.dealer.card_value > 19 or self.player.card_value > 19:
                continue
            break

    def prepare_embed(self, end: bool = False) -> disnake.Embed:
        em = disnake.Embed(color=utils.blurple)
        em.set_author(name=f'{self.user.display_name}\'s blackjack game', icon_url=self.user.display_avatar)
        em.set_footer(text='K, Q, J = 10  |  A = 1 or 11')
        em.add_field(
            f'{self.user.display_name} (Player)',
            f'Cards - {" ".join([str(card) for card in self.player.cards])}\n'
            f'Total - `{self.player.card_value}`'
        )
        if end is False:
            em.add_field(
                f'{self.bot.user.display_name} (Dealer)',
                f'Cards - {" ".join([str(card) for card in self.dealer.cards[0:-1]])} {hyperlink.format("?")}\n'
                f'Total - ` ? `'
            )
        else:
            em.add_field(
                f'{self.bot.user.display_name} (Dealer)',
                f'Cards - {" ".join([str(card) for card in self.dealer.cards])}\n'
                f'Total - `{self.dealer.card_value}`'
            )

        return em

    def disable_buttons(self):
        for btn in self.children:
            btn.disabled = True

    async def win(self, reason: str):
        data: Game = await Game.get(self.user.id)
        data.coins += self.bet_amount
        await data.commit()
        em = self.prepare_embed(end=True)
        em.description = f'**You Win! {reason}**\n' \
                         f'You won **{self.bet_amount:,}** 🪙 and now have a total of **{data.coins:,}** 🪙'
        em.color = utils.green
        self.disable_buttons()
        await self.message.edit(embed=em, view=self)
        self.stop()

    async def lose(self, reason: str):
        data: Game = await Game.get(self.user.id)
        data.coins -= self.bet_amount
        await data.commit()
        em = self.prepare_embed(end=True)
        em.description = f'**You Lost! {reason}**\n' \
                         f'You lost **{self.bet_amount:,}** 🪙 and now have a total of **{data.coins:,}** 🪙'
        em.color = utils.red
        self.disable_buttons()
        await self.message.edit(embed=em, view=self)
        self.stop()

    async def tie(self, reason: str):
        data: Game = await Game.get(self.user.id)
        em = self.prepare_embed(end=True)
        em.description = f'**You Tied! {reason}**\n' \
                         f'Your coins haven\'t changed. You still have **{data.coins:,}** 🪙'
        em.color = utils.yellow
        self.disable_buttons()
        await self.message.edit(embed=em, view=self)
        self.stop()

    def dealers_play(self):
        self.dealer.calculate_card_value()
        while self.dealer.card_value < 17:
            self.deck.give_random_card(self.dealer, 1)

    async def check_blackjack(self, end: bool = False):
        self.player.calculate_card_value()

        if end is True:
            self.dealers_play()
            if self.dealer.card_value > 21:
                return await self.win(
                    'The dealer went over 21 and busted.'
                )
            elif self.dealer.card_value == 21:
                return await self.lose(
                    'The dealer got to 21 before you.'
                )
            elif self.player.card_value > self.dealer.card_value:
                return await self.win(
                    f'You stood with a higher score (`{self.player.card_value}`) '
                    f'than the dealer (`{self.dealer.card_value}`)'
                )
            elif self.player.card_value < self.dealer.card_value:
                return await self.lose(
                    f'You stood with a lower score (`{self.player.card_value}`) '
                    f'than the dealer (`{self.dealer.card_value}`)'
                )
            elif self.player.card_value == self.dealer.card_value:
                return await self.tie(
                    f'Both you and the dealer had {self.player.card_value} cards.'
                )

        if self.player.card_value > 21:
            return await self.lose(
                'You went over 21 and busted.'
            )
        elif self.player.card_value == 21:
            return await self.win(
                'You got to 21.'
            )
        else:
            return await self.message.edit(embed=self.prepare_embed())

    @button(label='Hit', style=ButtonStyle.blurple)
    async def hit_btn(self, button: Button, inter: MessageInteraction):
        await inter.response.defer()

        self.deck.give_random_card(self.player, 1)
        await self.check_blackjack()

    @button(label='Stand', style=ButtonStyle.blurple)
    async def stand_btn(self, button: Button, inter: MessageInteraction):
        await inter.response.defer()

        await self.check_blackjack(end=True)

    @button(label='Forfeit', style=ButtonStyle.red)
    async def forfeit_btn(self, button: Button, inter: MessageInteraction):
        await inter.response.defer()

        data: Game = await Game.get(self.user.id)
        data.coins -= self.bet_amount
        await data.commit()
        em = self.prepare_embed(end=True)
        em.description = '**You ended the game.**\n' \
                         f'You lost **{self.bet_amount:,}** 🪙 and now have a total of **{data.coins:,}** 🪙'
        em.color = utils.yellow
        self.disable_buttons()
        await self.message.edit(embed=em, view=self)
        self.stop()

    async def on_timeout(self):
        data: Game = await Game.get(self.user.id)
        data.coins -= self.bet_amount
        await data.commit()
        em = self.prepare_embed(end=True)
        em.description = '**You didn\'t respond in time.**\n' \
                         f'You lost **{self.bet_amount:,}** 🪙 and now have a total of **{data.coins:,}** 🪙'
        em.color = utils.yellow
        self.disable_buttons()
        await self.message.edit(embed=em, view=self)

    async def interaction_check(self, interaction: MessageInteraction) -> bool:
        if interaction.author.id != self.user.id:
            await interaction.response.send_message(
                'You are not playing in this game! To start a blackjack game of your own please type `!game blackjack <amount>`',
                ephemeral=True
            )
            return False
        return True
