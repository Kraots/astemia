import disnake

dm_statuses = {
    'Open': 1097610034843750511, 'Ask': 1097610034843750510, 'Closed': 1097610034780831750
}

__all__ = (
    'DMButtonRoles',
)


class DMButtonRoles(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def handle_role(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        roles = [r for r in inter.author.roles if r.id not in dm_statuses.values()]
        role_id = dm_statuses[button.label]
        role = inter.guild.get_role(role_id)
        roles.append(role)
        await inter.author.edit(roles=roles)
        await inter.send(f'I have changed your dm status role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Open', custom_id='astemia:dm_statuses:open', row=0, style=disnake.ButtonStyle.blurple)
    async def open(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await self.handle_role(button, inter)

    @disnake.ui.button(label='Ask', custom_id='astemia:dm_statuses:ask', row=0, style=disnake.ButtonStyle.blurple)
    async def ask(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await self.handle_role(button, inter)

    @disnake.ui.button(label='Closed', custom_id='astemia:dm_statuses:closed', row=0, style=disnake.ButtonStyle.blurple)
    async def closed(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await self.handle_role(button, inter)
