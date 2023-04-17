import disnake

all_colour_roles = (
    1097610034998935563, 1097610034998935562, 1097610034927640615,
    1097610034927640614, 1097610034927640613, 1097610034927640612,
    1097610034927640611, 1097610034927640610, 1097610034927640609,
    1097610034927640608, 1097610034927640607, 1097610034927640606,
    1097610034843750519, 1097610034843750518, 1097610034843750517,
    1097610034843750516, 1097610034843750515, 1097610034843750514,
    1097610034843750513, 1097610034843750512  # The last one is owner only red
)

colour_roles = {
    'astemia:colour_roles:Madang': 1097610034998935563, 'astemia:colour_roles:Orchid': 1097610034998935562,
    'astemia:colour_roles:Primrose': 1097610034927640615, 'astemia:colour_roles:Ice_Cold': 1097610034927640614,
    'astemia:colour_roles:Perano': 1097610034927640613, 'astemia:colour_roles:Perfume': 1097610034927640612,
    'astemia:colour_roles:Wewak': 1097610034927640611, 'astemia:colour_roles:Illusion': 1097610034927640610,
    'astemia:colour_roles:Mandys_Pink': 1097610034927640609, 'astemia:colour_roles:White': 1097610034927640608,
    'astemia:colour_roles:Black': 1097610034927640607, 'astemia:colour_roles:Electric_Violet': 1097610034927640606,
    'astemia:colour_roles:Broom': 1097610034843750519, 'astemia:colour_roles:Screaming_Green': 1097610034843750518,
    'astemia:colour_roles:Red_Orange': 1097610034843750517, 'astemia:colour_roles:Dodger_Blue': 1097610034843750516,
    'astemia:colour_roles:Spring_Green': 1097610034843750515, 'astemia:colour_roles:Turquoise': 1097610034843750514,
    'astemia:colour_roles:Sunshade': 1097610034843750513
}

__all__ = (
    'ColourButtonRoles',
    'all_colour_roles',
)


class ColourButtonRoles(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label='Illusion', custom_id='astemia:colour_roles:Illusion', emoji='<:illusion:938412173846270004>')
    async def Illusion(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Black', custom_id='astemia:colour_roles:Black', emoji='<:black:938412174785785886>')
    async def Black(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Screaming Green', custom_id='astemia:colour_roles:Screaming_Green', emoji='<:screaming_green:938412175763050547>')
    async def Screaming_Green(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Electric Violet', custom_id='astemia:colour_roles:Electric_Violet', emoji='<:electric_violet:938412176723558431>')
    async def Electric_Violet(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Red Orange', custom_id='astemia:colour_roles:Red_Orange', emoji='<:red_orange:938412177944088647>')
    async def Red_Orange(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Dodger Blue', custom_id='astemia:colour_roles:Dodger_Blue', emoji='<:dodger_blue:938412178808135720>')
    async def Dodger_Blue(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Spring Green', custom_id='astemia:colour_roles:Spring_Green', emoji='<:spring_green:938412179290460191>')
    async def Spring_Green(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Madang', custom_id='astemia:colour_roles:Madang', emoji='<:madang:938412180511006720>')
    async def Madang(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Perfume', custom_id='astemia:colour_roles:Perfume', emoji='<:perfume:938412181534437446>')
    async def Perfume(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Ice Cold', custom_id='astemia:colour_roles:Ice_Cold', emoji='<:ice_cold:938412182411034654>')
    async def Ice_Cold(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Primrose', custom_id='astemia:colour_roles:Primrose', emoji='<:primrose:938412183262478377>')
    async def Primrose(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Orchid', custom_id='astemia:colour_roles:Orchid', emoji='<:orchid:938412192196350003>')
    async def Orchid(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Mandys Pink', custom_id='astemia:colour_roles:Mandys_Pink', emoji='<:mandys_pink:938412184302657566>')
    async def Mandys_Pink(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Perano', custom_id='astemia:colour_roles:Perano', emoji='<:perano:938412185762291812>')
    async def Perano(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Turquoise', custom_id='astemia:colour_roles:Turquoise', emoji='<:turquoise:938412186924109874>')
    async def Turquoise(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Wewak', custom_id='astemia:colour_roles:Wewak', emoji='<:wewak:938412188165632010>')
    async def Wewak(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Sunshade', custom_id='astemia:colour_roles:Sunshade', emoji='<:sunshade:938412189172265050>')
    async def Sunshade(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='White', custom_id='astemia:colour_roles:White', emoji='<:white:886669988558176306>')
    async def White(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Broom', custom_id='astemia:colour_roles:Broom', emoji='<:broom:938412190996774974>')
    async def Broom(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)
