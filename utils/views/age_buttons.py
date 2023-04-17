import disnake

all_age_roles = (
    1097610034780831749, 1097610034780831748, 1097610034780831747,
    1097610034780831746, 1097610034780831745, 1097610034780831744
)

# The age roles are not actually from 14 to 19 but different
# This is due to a change, and due to my laziness they'll stay that way
# for the custom id and for the code to still work with the old
# age roles message, however they'll appear the way they're supposed
# to when taking the respective roles as well as the proper age buttons.
age_roles = {
    'astemia:age_roles:14': 1097610034780831749, 'astemia:age_roles:15': 1097610034780831748,
    'astemia:age_roles:16': 1097610034780831747, 'astemia:age_roles:17': 1097610034780831746,
    'astemia:age_roles:18': 1097610034780831745, 'astemia:age_roles:19': 1097610034780831744
}

__all__ = (
    'AgeButtonRoles',
    'all_age_roles',
)


class AgeButtonRoles(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label='14', custom_id='astemia:age_roles:14', row=0, style=disnake.ButtonStyle.blurple)
    async def _14(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_age_roles]
        roles.append(interaction.guild.get_role(age_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Age role update.')
        await interaction.response.send_message(f'I have changed your age role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='15', custom_id='astemia:age_roles:15', row=0, style=disnake.ButtonStyle.blurple)
    async def _15(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_age_roles]
        roles.append(interaction.guild.get_role(age_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Age role update.')
        await interaction.response.send_message(f'I have changed your age role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='16', custom_id='astemia:age_roles:16', row=0, style=disnake.ButtonStyle.blurple)
    async def _16(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_age_roles]
        roles.append(interaction.guild.get_role(age_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Age role update.')
        await interaction.response.send_message(f'I have changed your age role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='17', custom_id='astemia:age_roles:17', row=1, style=disnake.ButtonStyle.blurple)
    async def _17(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_age_roles]
        roles.append(interaction.guild.get_role(age_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Age role update.')
        await interaction.response.send_message(f'I have changed your age role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='18', custom_id='astemia:age_roles:18', row=1, style=disnake.ButtonStyle.blurple)
    async def _18(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_age_roles]
        roles.append(interaction.guild.get_role(age_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Age role update.')
        await interaction.response.send_message(f'I have changed your age role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='19', custom_id='astemia:age_roles:19', row=1, style=disnake.ButtonStyle.blurple)
    async def _19(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_age_roles]
        roles.append(interaction.guild.get_role(age_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Age role update.')
        await interaction.response.send_message(f'I have changed your age role to `{button.label}`', ephemeral=True)
