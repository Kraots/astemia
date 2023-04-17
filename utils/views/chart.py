import disnake

from ..context import Context
from ..colours import blurple

__all__ = (
    'SelectChart',
)


class SelectWhoseData(disnake.ui.Select['SelectChart']):
    def __init__(self, user_label: str):
        super().__init__(placeholder='Select whose chart...', min_values=1, max_values=1)
        self.user_label = user_label
        self._fill_options()

    def _fill_options(self):
        self.add_option(label=self.user_label, value='user')
        self.add_option(label='Server', value='server')

    async def callback(self, interaction: disnake.MessageInteraction):
        await interaction.response.defer()

        if self.view is None:
            return

        value = self.values[0]
        old_value = self.view.whose_data
        self.view.whose_data = value
        self.view.viewing = self.view.viewing.replace(old_value, value)

        if 'user' in self.view.viewing:
            file = disnake.File(
                f'stats_chart/{self.view.viewing}-{self.view.user.id}.png',
                f'{self.view.viewing}-{self.view.user.id}.png'
            )
        else:
            file = disnake.File(
                f'stats_chart/{self.view.viewing}.png',
                f'{self.view.viewing}.png'
            )

        em = disnake.Embed(
            title=(self.view.user.display_name + '\'s activity stats' if self.view.whose_data == 'user' else
                   'Astemia\'s stats'),
            color=blurple
        )
        em.set_image(url=f'attachment://{file.filename}')
        await self.view.message.edit(embed=em, view=self.view, file=file)


class SelectTimeFrame(disnake.ui.Select['SelectChart']):
    def __init__(self):
        super().__init__(placeholder='Select time chart...', min_values=1, max_values=1)
        self._fill_options()

    def _fill_options(self):
        self.add_option(label='Daily', value='daily')
        self.add_option(label='Weekly', value='weekly')
        self.add_option(label='Monthly', value='monthly')
        self.add_option(label='Yearly', value='yearly')

    async def callback(self, interaction: disnake.MessageInteraction):
        await interaction.response.defer()

        if self.view is None:
            return

        _value = self.values[0]
        value = self.view.whose_data + '-' + _value
        self.view.viewing = value

        if 'user' in self.view.viewing:
            file = disnake.File(
                f'stats_chart/{self.view.viewing}-{self.view.user.id}.png',
                f'{self.view.viewing}-{self.view.user.id}.png'
            )
        else:
            file = disnake.File(
                f'stats_chart/{self.view.viewing}.png',
                f'{self.view.viewing}.png'
            )

        em = disnake.Embed(
            title=(self.view.user.display_name + '\'s activity stats' if self.view.whose_data == 'user' else
                   'Astemia\'s stats'),
            color=blurple
        )
        em.set_image(url=f'attachment://{file.filename}')
        await self.view.message.edit(embed=em, view=self.view, file=file)


class SelectChart(disnake.ui.View):
    message: disnake.Message
    whose_data: str

    def __init__(
        self,
        ctx: Context,
        user: disnake.Member
    ):
        super().__init__(timeout=300.0)
        self.ctx = ctx
        self.user = user
        self.add_item(SelectTimeFrame())
        self.add_item(SelectWhoseData(user.display_name))

        self.whose_data = 'user'
        self.viewing: str | None = 'user-daily'

    async def interaction_check(self, inter: disnake.MessageInteraction) -> bool:
        if inter.user and inter.user.id in (self.ctx.bot._owner_id, self.ctx.author.id):
            return True
        await inter.response.send_message(
            'This pagination menu cannot be controlled by you, sorry!',
            ephemeral=True
        )
        return False

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

    async def on_error(self, error, item, inter):
        await self.ctx.bot.inter_reraise(inter, item, error)

    async def start(self):
        file = disnake.File(
            f'stats_chart/user-daily-{self.user.id}.png',
            f'user-daily-{self.user.id}.png'
        )
        em = disnake.Embed(
            title=self.user.display_name + '\'s activity stats',
            color=blurple
        )
        em.set_image(url=f'attachment://{file.filename}')
        await self.message.edit(content=None, embed=em, view=self, file=file)
