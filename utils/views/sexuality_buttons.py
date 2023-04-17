import disnake

all_sexuality_roles = (
    1097610034734702594, 1097610034734702593, 1097610034734702592,
    1097610034701144153, 1097610034701144152, 1097610034701144151,
    1097610034701144150
)

sexuality_roles = {
    'astemia:sexuality_roles:Straight': 1097610034734702594, 'astemia:sexuality_roles:Bisexual': 1097610034734702593,
    'astemia:sexuality_roles:Gay': 1097610034734702592, 'astemia:sexuality_roles:Lesbian': 1097610034701144153,
    'astemia:sexuality_roles:Asexual': 1097610034701144152, 'astemia:sexuality_roles:Queer': 1097610034701144151,
    'astemia:sexuality_roles:Other-Sexuality': 1097610034701144150
}

__all__ = (
    'SexualityButtonRoles',
    'all_sexuality_roles',
)


class SexualityButtonRoles(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label='Straight', custom_id='astemia:sexuality_roles:Straight', row=0, style=disnake.ButtonStyle.blurple)
    async def Straight(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_sexuality_roles]
        roles.append(interaction.guild.get_role(sexuality_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Sexuality role update.')
        await interaction.response.send_message(f'I have changed your sexuality role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Gay', custom_id='astemia:sexuality_roles:Gay', row=0, style=disnake.ButtonStyle.blurple)
    async def Gay(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_sexuality_roles]
        roles.append(interaction.guild.get_role(sexuality_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Sexuality role update.')
        await interaction.response.send_message(f'I have changed your sexuality role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Lesbian', custom_id='astemia:sexuality_roles:Lesbian', row=0, style=disnake.ButtonStyle.blurple)
    async def Lesbian(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_sexuality_roles]
        roles.append(interaction.guild.get_role(sexuality_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Sexuality role update.')
        await interaction.response.send_message(f'I have changed your sexuality role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Bisexual', custom_id='astemia:sexuality_roles:Bisexual', row=1, style=disnake.ButtonStyle.blurple)
    async def Bisexual(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_sexuality_roles]
        roles.append(interaction.guild.get_role(sexuality_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Sexuality role update.')
        await interaction.response.send_message(f'I have changed your sexuality role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Asexual', custom_id='astemia:sexuality_roles:Asexual', row=1, style=disnake.ButtonStyle.blurple)
    async def Asexual(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_sexuality_roles]
        roles.append(interaction.guild.get_role(sexuality_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Sexuality role update.')
        await interaction.response.send_message(f'I have changed your sexuality role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Queer', custom_id='astemia:sexuality_roles:Queer', row=1, style=disnake.ButtonStyle.blurple)
    async def Queer(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_sexuality_roles]
        roles.append(interaction.guild.get_role(sexuality_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Sexuality role update.')
        await interaction.response.send_message(f'I have changed your sexuality role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Other Sexuality', custom_id='astemia:sexuality_roles:Other-Sexuality', row=2, style=disnake.ButtonStyle.blurple)
    async def Other_Sexuality(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_sexuality_roles]
        roles.append(interaction.guild.get_role(sexuality_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Sexuality role update.')
        await interaction.response.send_message(f'I have changed your sexuality role to `{button.label}`', ephemeral=True)
