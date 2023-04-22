from dateutil.relativedelta import relativedelta
from datetime import datetime

import disnake
from disnake.ext import commands
from disnake.ui import Modal, TextInput
from disnake import (
    AppCmdInter,
    TextInputStyle,
    ModalInteraction,
    Embed
)

import utils
from utils import Poll

from main import Astemia


class RecommendModal(Modal):
    def __init__(self):
        components = [
            TextInput(
                label='Type',
                custom_id='recommendation-type',
                placeholder='Anime/Webtoon/Manga/Manhwa/Manhua...',
                style=TextInputStyle.short,
                max_length=30
            ),
            TextInput(
                label='Title',
                custom_id='recommendation-title',
                placeholder='The title of your recommendation...',
                style=TextInputStyle.short,
                max_length=100
            ),
            TextInput(
                label='Synopsis',
                custom_id='recommendation-synopsis',
                placeholder='A short synopsis of your recommendation...',
                style=TextInputStyle.paragraph,
                max_length=1024
            ),
            TextInput(
                label='Source/Website to watch/read it on',
                custom_id='recommendation-source',
                placeholder='The link to a website where to watch/read this recommendation...',
                style=TextInputStyle.short,
                max_length=300
            ),
            TextInput(
                label='Status',
                custom_id='recommendation-status',
                placeholder='Ongoing/Canceled/Hiatus...',
                style=TextInputStyle.short,
                max_length=15
            )
        ]
        super().__init__(
            title='Make Recommendation',
            components=components
        )

    async def callback(self, inter: ModalInteraction):
        channel = inter.guild.get_channel(utils.Channels.recommendations)
        values_ = inter.text_values.values()
        fields = ['Type', 'Title', 'Synopsis', 'Source/Website to watch/read it on', 'Status']
        values = zip(fields, values_)
        em = Embed(
            color=inter.author.color,
        )
        for k, v in values:
            if k == 'Source/Website to watch/read it on':
                match = utils.URL_REGEX.findall(v)
                if not match:
                    return await inter.send(
                        'You must give a valid url for where to watch/read this! '
                        '(Not the name or the site or just the site itself, but the '
                        'full url to this specific recommendation)',
                        ephemeral=True
                    )
            em.add_field(
                k,
                v,
                inline=False
            )
        em.set_footer(
            text=f'Recommendation by: {utils.format_name(inter.author)}',
            icon_url=inter.author.display_avatar
        )
        m = await channel.send(embed=em, view=utils.TrashButtonDelete())
        await inter.send(
            'Recommendation succesfully submitted.',
            ephemeral=True,
            view=utils.UrlButton('Jump!', m.jump_url)
        )


class PollDropdown(disnake.ui.Select):
    def __init__(self, bot: Astemia, options, title, min_choices, max_choices, votes, voted):
        self.poll_options = []
        self.title = title
        self.str_options = options
        self.votes = votes
        self.voted = voted
        self.bot = bot

        for i in options:
            self.poll_options.append(disnake.SelectOption(label=i))

        super().__init__(
            placeholder="Click here to vote...",
            min_values=min_choices,
            max_values=max_choices,
            options=self.poll_options,
            custom_id="poll"
        )

    async def callback(self, inter: disnake.MessageInteraction):
        if inter.author.id in self.voted:
            return await inter.send(
                f"You have already voted in [this poll!]({inter.message.id})",
                ephemeral=True
            )

        self.voted.append(inter.author.id)
        votes_to_update = []
        empty = "<:poll_empty:1009506776158322688>"
        one_quarter = "<:poll_one_quarter:1009506782017765416>"
        half = "<:poll_half:1009506780340039770>"
        three_quarters = "<:poll_three_quarters:1009506783691276319>"
        full = "<:poll_full:1009506778632949760>"

        old_votes = 0
        for i in self.votes:
            old_votes += i

        for i in self.values:
            print(self.str_options)
            print(i)
            index = self.str_options.index(i)
            votes_to_update.append(index)

        for i in votes_to_update:
            self.votes[i] += 1

        total_votes = 0
        for i in self.votes:
            total_votes += i

        data: Poll = await self.bot.db.get('polls', inter.message.id)
        data.votes = self.votes
        data.voted = self.voted
        await data.commit()

        poll_channel = self.bot.get_channel(utils.Channels.polls)
        embed = (await poll_channel.fetch_message(inter.message.id)).embeds[0]
        embed.description = embed.description.replace(
            f"Total votes: {old_votes}",
            f"Total votes: {total_votes}"
        )
        embed.clear_fields()

        for count, i in enumerate(self.poll_options):
            filled = self.votes[count] / total_votes * 5
            filled_remainder = round(filled % 1, 2)
            if filled_remainder < 0.1:
                filled_partial = ""
            elif filled_remainder <= 0.35:
                filled_partial = one_quarter
            elif filled_remainder <= 0.65:
                filled_partial = half
            elif filled_remainder <= 0.9:
                filled_partial = three_quarters
            else:
                filled_partial = full

            blocks_filled = f"{full * int(filled)}{filled_partial}"
            block_count = int(filled)

            if filled_partial != "":
                block_count += 1
            blocks_empty = empty * (5 - block_count)
            total_blocks = f"{blocks_filled}{blocks_empty}"

            if int(self.votes[count]) >= 1 and total_blocks == f"{empty * 5}":
                total_blocks = f"{one_quarter}{empty * 4}"

            winner = " <:agree:938412298769432586>" if int(self.votes[count]) == max(self.votes) else ""
            embed.add_field(
                name=i,
                value=f"{total_blocks} ({self.votes[count]}{winner})"
            )
        await inter.response.edit_message(embed=embed)


class PollView(disnake.ui.View):
    def __init__(self, bot, poll_options, title, min_choices, max_choices, votes, voted):
        super().__init__(timeout=None)
        self.add_item(PollDropdown(
            bot, poll_options, title, min_choices, max_choices, votes, voted))


class SlashCommands(commands.Cog):
    def __init__(self, bot: Astemia):
        self.bot = bot
        self.loaded_polls = False

    @commands.slash_command(name='colours', description='Change your colour!')
    async def change_colour(self, inter: AppCmdInter):
        if inter.author.id == self.bot._owner_id:
            view = utils.SlashColours(inter, is_owner=True)
            await inter.response.send_message('**Please use me master 😩**', view=view, ephemeral=True)
        else:
            view = utils.SlashColours(inter)
            await inter.response.send_message('**Please use the select menu below:**', view=view, ephemeral=True)

    @commands.slash_command(name='recommend', description='Recommend an anime/manga/webtoon/manhwa.')
    async def recommend(self, inter: AppCmdInter):
        await inter.response.send_modal(RecommendModal())

    @commands.slash_command()
    async def poll(self, inter):
        pass

    @poll.sub_command(name='create')
    async def poll_create(
        self,
        inter: disnake.ApplicationCommandInteraction,
        title: str,
        options: str,
        duration: str,
        min_choices: int = commands.Param(default=1, ge=1, le=24),
        max_choices: int = commands.Param(default=1, ge=1, le=25)):  # noqa
        """Make a poll
        Parameters
        ----------
        title: str
            The title of the poll
        options: str
            The options for the poll, *separated by commas*
        duration: str
            The duration of the poll
        min_choices: int
            The minimum number of choices
        max_choices: int
            The maximum number of choices
        """

        if not any([role for role in inter.author.roles if role.id in utils.StaffRoles.all]):
            if inter.author.id != self.bot._owner_id:
                return await inter.send('Only staff members can use this command.', ephemeral=True)

        duration = await utils.TimeConverter.convert(duration)

        poll_options = options.split(",")[:25]
        poll_options = [i.strip() for i in poll_options]
        poll_options = [i[:25] for i in poll_options]

        votes = []
        for i in poll_options:
            votes.append(0)

        expire_date = datetime.utcnow() + relativedelta(seconds=duration)
        embed = disnake.Embed(
            title=title,
            color=utils.green,
            description=f"Poll ends {utils.format_dt(expire_date, 'F')} ({utils.format_dt(expire_date, 'R')})"
                        "\n\nTotal votes: 0"
        )
        embed.set_footer(text='Once you voted you cannot remove your vote or vote again! Choose wisely.')
        for i in poll_options:
            embed.add_field(
                name=i,
                value=f"{'<:poll_empty:1009506776158322688>' * 5} (0)"
            )
            embed.set_author(
                name=f"Poll by: {inter.author}",
                icon_url=inter.author.display_avatar.url
            )

        channel = self.bot.get_channel(utils.Channels.polls)
        view = PollView(self.bot, poll_options, title, min_choices, max_choices, votes, [])
        message = await channel.send(content=None, embed=embed, view=view)
        view.message_id = message.id

        await self.bot.db.add('polls', Poll(
            message_id=message.id,
            title=title.lower(),
            options=poll_options,
            votes=votes,
            voted=[],
            min_choices=min_choices,
            max_choices=max_choices,
            expire_date=expire_date
        ))

        await inter.send(
            'Poll created.',
            view=utils.UrlButton('See poll', message.jump_url)
        )

    @poll.sub_command(name='close')
    async def close_poll(self, inter: disnake.ApplicationCommandInteraction, title: str):
        """Close a poll, must be poll author or a mod
        Parameters
        ----------
        title: str
            The title of the poll to close
        """

        if not any([role for role in inter.author.roles if role.id in utils.StaffRoles.all]):
            if inter.author.id != self.bot._owner_id:
                return await inter.send('Only staff members can use this command.', ephemeral=True)

        poll: Poll = await self.bot.db.find_one({'title': title})
        channel = self.bot.get_channel(utils.Channels.polls)
        message = await channel.fetch_message(poll.message_id)
        embed = message.embeds[0]
        embed.color = utils.red
        await message.edit(view=None, embed=embed)
        await self.bot.db.delete('reminders', {'_id': poll.pk})

        await inter.send(
            "Poll closed.",
            view=utils.UrlButton('See Poll', message.jump_url)
        )

    @close_poll.autocomplete("title")
    async def autocomplete_title(self, inter: disnake.ApplicationCommandInteraction, user_input: str):
        user_input = user_input.lower()
        titles = [poll.title for poll in await self.bot.db.find('reminders')]
        return utils.finder(user_input, titles, lazy=False)[:25]

    @commands.Cog.listener()
    async def on_ready(self):
        if self.loaded_polls is True:
            self.loaded_polls = True
            return

        for poll in await self.bot.db.find('polls'):
            view = PollView(
                self.bot,
                poll.options,
                poll.title,
                poll.min_choices,
                poll.max_choices,
                poll.votes,
                poll.voted
            )
            self.bot.add_view(view, message_id=poll.message_id)


def setup(bot: Astemia):
    bot.add_cog(SlashCommands(bot))
