import disnake

import utils

__all__ = (
    'SlashColours',
)

all_colours_dict = {
    'Madang': 1097610034998935563, 'Orchid': 1097610034998935562, 'Primrose': 1097610034927640615,
    'Ice Cold': 1097610034927640614, 'Perano': 1097610034927640613, 'Perfume': 1097610034927640612,
    'Wewak': 1097610034927640611, 'Illusion': 1097610034927640610, 'Mandys Pink': 1097610034927640609,
    'White': 1097610034927640608, 'Black': 1097610034927640607, 'Electric Violet': 1097610034927640606,
    'Broom': 1097610034843750519, 'Screaming Green': 1097610034843750518, 'Red Orange': 1097610034843750517,
    'Dodger Blue': 1097610034843750516, 'Spring Green': 1097610034843750515, 'Turquoise': 1097610034843750514,
    'Sunshade': 1097610034843750513, 'Owner Only Red': 1097610034843750512
}


class SlashColoursSelect(disnake.ui.Select['SlashColours']):
    def __init__(self, *, is_owner: bool, placeholder: str = 'Select a colour...'):
        super().__init__(placeholder=placeholder, min_values=1, max_values=1)
        self.is_owner = is_owner
        self._fill_options()

    def _fill_options(self):
        if self.is_owner:
            self.add_option(label='Owner Only Red', emoji='<:owner_only_red:938412193320411167>')
        self.add_option(label='Illusion', emoji='<:illusion:938412173846270004>')
        self.add_option(label='Black', emoji='<:black:938412174785785886>')
        self.add_option(label='Screaming Green', emoji='<:screaming_green:938412175763050547>')
        self.add_option(label='Electric Violet', emoji='<:electric_violet:938412176723558431>')
        self.add_option(label='Red Orange', emoji='<:red_orange:938412177944088647>')
        self.add_option(label='Dodger Blue', emoji='<:dodger_blue:938412178808135720>')
        self.add_option(label='Spring Green', emoji='<:spring_green:938412179290460191>')
        self.add_option(label='Madang', emoji='<:madang:938412180511006720>')
        self.add_option(label='Perfume', emoji='<:perfume:938412181534437446>')
        self.add_option(label='Ice Cold', emoji='<:ice_cold:938412182411034654>')
        self.add_option(label='Primrose', emoji='<:primrose:938412183262478377>')
        self.add_option(label='Orchid', emoji='<:orchid:938412192196350003>')
        self.add_option(label='Mandys Pink', emoji='<:mandys_pink:938412184302657566>')
        self.add_option(label='Perano', emoji='<:perano:938412185762291812>')
        self.add_option(label='Turquoise', emoji='<:turquoise:938412186924109874>')
        self.add_option(label='Wewak', emoji='<:wewak:938412188165632010>')
        self.add_option(label='Sunshade', emoji='<:sunshade:938412189172265050>')
        self.add_option(label='White', emoji='<:white:886669988558176306>')
        self.add_option(label='Broom', emoji='<:broom:938412190996774974>')

    async def callback(self, interaction: disnake.MessageInteraction):
        assert self.view is not None
        value = self.values[0]
        roles = [role for role in interaction.author.roles if role.id not in utils.all_colour_roles]
        roles.append(interaction.guild.get_role(all_colours_dict[value]))
        await interaction.author.edit(roles=roles, reason='Colour role update via select menu.')
        await interaction.response.edit_message(content=f'Changed your colour to `{value}`')


class SlashColours(disnake.ui.View):
    def __init__(self, inter, *, is_owner: bool = False):
        super().__init__(timeout=None)
        self.inter = inter
        placeholder = 'Select a colour master...' if is_owner is True else None
        self.add_item(SlashColoursSelect(is_owner=is_owner, placeholder=placeholder))
