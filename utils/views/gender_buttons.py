import disnake

all_gender_roles = (
    1097610034776637623, 1097610034776637622,
    1097610034776637621, 1097610034734702601,
    1097610034734702600
)

gender_roles = {
    'astemia:gender_roles:Male': 1097610034776637623, 'astemia:gender_roles:Female': 1097610034776637622,
    'astemia:gender_roles:Trans-Male': 1097610034776637621, 'astemia:gender_roles:Trans-Female': 1097610034734702601,
    'astemia:gender_roles:Other-Gender': 1097610034734702600
}

__all__ = (
    'GenderButtonRoles',
    'all_gender_roles',
)


class GenderButtonRoles(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label='Cis Male', custom_id='astemia:gender_roles:Male', row=0, style=disnake.ButtonStyle.blurple)
    async def Cis_Male(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_gender_roles]
        roles.append(interaction.guild.get_role(gender_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Gender role update.')
        await interaction.response.send_message(f'I have changed your gender role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Cis Female', custom_id='astemia:gender_roles:Female', row=0, style=disnake.ButtonStyle.blurple)
    async def Cis_Female(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_gender_roles]
        roles.append(interaction.guild.get_role(gender_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Gender role update.')
        await interaction.response.send_message(f'I have changed your gender role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Trans Male', custom_id='astemia:gender_roles:Trans-Male', row=1, style=disnake.ButtonStyle.blurple)
    async def Trans_Male(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_gender_roles]
        roles.append(interaction.guild.get_role(gender_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Gender role update.')
        await interaction.response.send_message(f'I have changed your gender role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Trans Female', custom_id='astemia:gender_roles:Trans-Female', row=1, style=disnake.ButtonStyle.blurple)
    async def Trans_Female(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_gender_roles]
        roles.append(interaction.guild.get_role(gender_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Gender role update.')
        await interaction.response.send_message(f'I have changed your gender role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Other Gender', custom_id='astemia:gender_roles:Other-Gender', row=2, style=disnake.ButtonStyle.blurple)
    async def Other_Gender(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_gender_roles]
        roles.append(interaction.guild.get_role(gender_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Gender role update.')
        await interaction.response.send_message(f'I have changed your gender role to `{button.label}`', ephemeral=True)
