import disnake

all_age_roles = (
    1095441108194054378, 1095441292454019194, 1095441513426731078,
    1095441634302374059, 1095441764531306636, 1095441903442460772
)

# The age roles are not actually from 14 to 19 but different
# This is due to a change, and due to my laziness they'll stay that way
# for the custom id and for the code to still work with the old
# age roles message, however they'll appear the way they're supposed
# to when taking the respective roles as well as the proper age buttons.
age_roles = {
    'astemia:age_roles:15': 1095441108194054378, 'astemia:age_roles:16': 1095441292454019194,
    'astemia:age_roles:17': 1095441513426731078, 'astemia:age_roles:18': 1095441634302374059,
    'astemia:age_roles:19': 1095441764531306636, 'astemia:age_roles:20+': 1095441903442460772
}

__all__ = (
    'AgeButtonRoles',
    'all_age_roles',
)


class AgeButtonRoles(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label='15', custom_id='astemia:age_roles:15', row=0, style=disnake.ButtonStyle.blurple)
    async def _14(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_age_roles]
        roles.append(interaction.guild.get_role(age_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Age role update.')
        await interaction.response.send_message(f'I have changed your age role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='16', custom_id='astemia:age_roles:16', row=0, style=disnake.ButtonStyle.blurple)
    async def _15(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_age_roles]
        roles.append(interaction.guild.get_role(age_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Age role update.')
        await interaction.response.send_message(f'I have changed your age role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='17', custom_id='astemia:age_roles:17', row=0, style=disnake.ButtonStyle.blurple)
    async def _16(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_age_roles]
        roles.append(interaction.guild.get_role(age_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Age role update.')
        await interaction.response.send_message(f'I have changed your age role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='18', custom_id='astemia:age_roles:18', row=1, style=disnake.ButtonStyle.blurple)
    async def _17(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_age_roles]
        roles.append(interaction.guild.get_role(age_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Age role update.')
        await interaction.response.send_message(f'I have changed your age role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='19', custom_id='astemia:age_roles:19', row=1, style=disnake.ButtonStyle.blurple)
    async def _18(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_age_roles]
        roles.append(interaction.guild.get_role(age_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Age role update.')
        await interaction.response.send_message(f'I have changed your age role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='20+', custom_id='astemia:age_roles:20+', row=1, style=disnake.ButtonStyle.blurple)
    async def _19(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_age_roles]
        roles.append(interaction.guild.get_role(age_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Age role update.')
        await interaction.response.send_message(f'I have changed your age role to `{button.label}`', ephemeral=True)
