import asyncio
import textwrap

from datetime import datetime

import disnake
from disnake import AppCmdInter
from disnake.ext import commands

import utils
from utils import Tags

from main import Astemia


async def tag_name(inter: disnake.ApplicationCommandInteraction, argument: str):
    converted = await utils.clean_inter_content()(inter, argument)
    lower = converted.lower().strip()

    if not lower:
        raise commands.BadArgument('Missing tag name.')

    if len(lower) > 50:
        raise commands.BadArgument('Tag name must be less than 50 characters.')
    elif len(lower) < 3:
        raise commands.BadArgument('Tag must be greater than 3 characters.')
    elif lower.isnumeric():
        raise commands.BadArgument('Tag must not be digits.')

    return lower


class InteractiveTagCreation(disnake.ui.View):
    def __init__(
        self,
        bot: Astemia,
        original_interaction: AppCmdInter,
        edit: Tags = None
    ):
        super().__init__(timeout=300.0)
        self.bot = bot
        self.original_inter = original_interaction
        self.author = original_interaction.author
        self._edit = edit
        self.aborted = False

        if edit:
            self.remove_item(self.set_name)
            self.name = edit.name
            self.content = edit.content
            self.attachment = edit.attachment
        else:
            self.name = self.content = self.attachment = None

    async def on_error(self, error: Exception, item, interaction: disnake.MessageInteraction) -> None:
        if isinstance(error, asyncio.TimeoutError):
            if interaction.response.is_done():
                method = self.message.edit
            else:
                method = interaction.response.edit_message
            await method(content='You took too long. Goodbye.', view=None, embed=None)
            return self.stop()
        raise error

    async def interaction_check(self, inter: disnake.MessageInteraction) -> bool:
        if inter.author.id != self.author.id:
            await inter.send_message(f'Only `{self.author}` can use the buttons on this message.', ephemeral=True)
            return False
        return True

    def lock_all(self):
        for child in self.children:
            if child.label == 'Abort':
                continue
            child.disabled = True

    def unlock_all(self):
        for child in self.children:
            if child.label == 'Confirm':
                if self._edit:
                    if self._edit.content != self.content:
                        child.disabled = False
                        continue
                    if self._edit.attachment != self.attachment:
                        child.disabled = False
                        continue

                elif self.name is not None and (
                    (self.content is not None) or
                    (self.attachment is not None)
                ):
                    child.disabled = False
                else:
                    child.disabled = True
            else:
                child.disabled = False

    def prepare_embed(self):
        em = disnake.Embed(title='Tag creation', color=utils.blurple)
        em.add_field(name='Name', value=str(self.name), inline=False)
        em.add_field(name='Content', value=textwrap.shorten(str(self.content), 1024), inline=False)
        if self.attachment != 'None':
            em.set_image(self.attachment)

        if len(str(self.content)) > 1024:
            em.description = '\n**Hint:** Tag content reached embed field limitation, this will not affect the content itself.'
        return em

    @disnake.ui.button(label='Name', style=disnake.ButtonStyle.blurple)
    async def set_name(self, button: disnake.Button, inter: disnake.MessageInteraction):
        self.lock_all()
        msg_content = 'Cool, let\'s make a name. Send the tag name in the next message...'
        await inter.response.edit_message(content=msg_content, view=self)

        msg = await self.bot.wait_for(
            'message',
            timeout=60.0,
            check=lambda m: m.author.id == self.author.id and m.channel.id == inter.channel.id
        )
        if self.is_finished():
            return

        content = None
        try:
            name = await tag_name(inter, msg.content)
        except commands.BadArgument as e:
            content = f'{e}. Press "Name" to retry.'
        else:
            tag = await self.bot.db.find_one('tags', {'name': name})
            if tag is None:
                self.name = name
                self.remove_item(button)
            else:
                content = 'A tag with that name already exists.'

        self.unlock_all()
        await self.message.edit(content=content, embed=self.prepare_embed(), view=self)

    @disnake.ui.button(label='Content', style=disnake.ButtonStyle.blurple)
    async def set_content(self, button: disnake.Button, inter: disnake.MessageInteraction):
        self.lock_all()
        msg_content = f'Cool, let\'s {"edit the" if self._edit else "make a"} content. Send the tag content in the next message...'

        await inter.response.edit_message(content=msg_content, view=self)
        msg = await self.bot.wait_for(
            'message',
            timeout=300.0,
            check=lambda m: m.author.id == self.author.id and m.channel.id == inter.channel.id
        )
        if self.is_finished():
            return

        if msg.content:
            clean_content = await utils.clean_inter_content()(inter, msg.content)
        else:
            clean_content = msg.content

        if msg.attachments:
            clean_content += f'\n{msg.attachments[0].url}'

        c = None
        if len(clean_content) > 4000:
            c = 'Tag content is a maximum of 4000 characters.'
        else:
            self.content = clean_content

        self.unlock_all()
        await self.message.edit(content=c, embed=self.prepare_embed(), view=self)

    @disnake.ui.button(label='Image', style=disnake.ButtonStyle.blurple)
    async def set_attachment(self, button: disnake.Button, inter: disnake.MessageInteraction):
        self.lock_all()
        msg_content = f'Cool, let\'s {"edit the" if self._edit else "set an"} image. ' \
                      'Send the tag image in the next message...'

        await inter.response.edit_message(content=msg_content, view=self)
        msg: disnake.Message = await self.bot.wait_for(
            'message',
            timeout=300.0,
            check=lambda m: m.author.id == self.author.id and m.channel.id == inter.channel.id
        )
        if self.is_finished():
            return

        c = None
        if msg.attachments:
            self.attachment = msg.attachments[0].url
        else:
            c = 'You didn\'t send an image. It must be from your gallery.'

        self.unlock_all()
        await self.message.edit(content=c, embed=self.prepare_embed(), view=self)

    @disnake.ui.button(label='Confirm', style=disnake.ButtonStyle.green)
    async def confirm(self, button: disnake.Button, inter: disnake.MessageInteraction):
        if self._edit and self._edit.content == self.content and self._edit.attachment == self.attachment:
            return await inter.response.edit_message(
                content='Content and attachment still the same...\n'
                        'Hint: edit it by pressing "Content" or "Attachment"'
            )
        for child in self.children:
            child.disabled = True
        await inter.response.edit_message(view=self)
        self.stop()

    @disnake.ui.button(label='Abort', style=disnake.ButtonStyle.red)
    async def cancel(self, button: disnake.Button, inter: disnake.MessageInteraction):
        await inter.response.edit_message(
            content=f'Tag {"edit" if self._edit else "creation"} aborted.',
            view=None,
            embed=None
        )
        self.aborted = True
        self.stop()


class _Tags(commands.Cog, name='Tags'):

    def __init__(self, bot: Astemia):
        self.bot = bot

    @property
    def display_emoji(self) -> str:
        return '🏷️'

    async def check_channel(self, inter: AppCmdInter):
        if inter.author.id != self.bot._owner_id:
            if inter.channel.id not in (
                utils.Channels.bots, utils.Channels.bot_commands
            ):
                await inter.response.send_message(
                    f'This command can only be used in <#{utils.Channels.bots}>',
                    ephemeral=True
                )
                raise commands.CheckFailure
            else:
                await inter.response.defer()
        else:
            await inter.response.defer()

    @commands.slash_command(name='tag')
    async def base_tag(*_):
        pass

    @base_tag.sub_command(name='create')
    async def create_tag(self, inter: AppCmdInter):
        """Create a tag."""

        await self.check_channel(inter)

        data = await utils.Level.get(inter.author.id)
        if data is None:
            return await inter.send(
                'You need to be level 30 or above in order '
                'to create tags.',
                ephemeral=True
            )

        lvl = 0
        xp = data.xp
        while True:
            if xp < ((50 * (lvl**2)) + (50 * (lvl - 1))):
                break
            lvl += 1
        xp -= ((50 * ((lvl - 1)**2)) + (50 * (lvl - 1)))
        if xp < 0:
            lvl = lvl - 1

        if lvl < 30:
            return await inter.send(
                'You need to be level 30 or above in order '
                'to create tags.',
                ephemeral=True
            )

        view = InteractiveTagCreation(self.bot, inter)
        await inter.send(embed=view.prepare_embed(), view=view)
        view.message = await inter.original_message()

        if await view.wait():
            return await view.message.edit(
                content='You took too long. Goodbye.',
                view=None,
                embed=None
            )
        else:
            if view.aborted:
                return
            await view.message.edit(view=None)

        if view.content is None:
            view.content = 'None'
        elif view.attachment is None:
            view.attachment = 'None'

        tag = Tags(
            name=view.name,
            content=view.content,
            attachment=view.attachment,
            owned_by=inter.author.id,
            created_at=datetime.now(),
            uses=0
        )

        await self.bot.db.add('tags', tag)

        await inter.send(f'Tag `{tag.name}` successfully created.')

    @base_tag.sub_command(name='edit')
    async def tag_edit(
        self,
        inter: AppCmdInter,
        tag_name: str = commands.Param(
            description='The name of the tag to edit'
        )
    ):
        """Edit a tag that you own."""

        await self.check_channel(inter)

        tag_name = tag_name.lower()
        tag: Tags = await self.bot.db.find_one('tags', {'name': tag_name})
        if tag is None:
            return await inter.send(f'Tag `{tag_name}` not found.', ephemeral=True)

        if tag.owned_by != inter.author.id and inter.author.id != self.bot._owner_id:
            return await inter.send(
                'You do not own that tag.',
                ephemeral=True
            )

        view = InteractiveTagCreation(self.bot, inter, tag)
        await inter.send(embed=view.prepare_embed(), view=view)
        view.message = await inter.original_message()

        if await view.wait():
            return await view.message.edit(
                content='You took too long. Goodbye.',
                view=None,
                embed=None
            )
        else:
            if view.aborted:
                return
            await view.message.edit(view=None)

        tag.content = view.content
        tag.attachment = view.attachment
        await tag.commit()

        await inter.send(f'Tag `{view.name}` successfully updated.')

    @tag_edit.autocomplete('tag_name')
    async def tag_edit_autocomp(self, inter: AppCmdInter, string: str):
        string = string.lower()
        tags = [tag.name for tag in await self.bot.db.find('tags')]
        return utils.finder(string, tags, lazy=False)[:25]

    @base_tag.sub_command(name='delete')
    async def tag_delete(
        self,
        inter: AppCmdInter,
        tag_name: str = commands.Param(
            description='The name of the tag to delete'
        )
    ):
        """Delete a tag that you own."""

        await self.check_channel(inter)

        tag_name = tag_name.lower()
        tag: Tags = await self.bot.db.find_one('tags', {'name': tag_name})
        if tag is None:
            return await inter.send(f'Tag `{tag_name}` not found.', ephemeral=True)

        if tag.owned_by != inter.author.id and inter.author.id != self.bot._owner_id:
            return await inter.send(
                'You do not own that tag.',
                ephemeral=True
            )

        await self.bot.db.delete('tags', {'name': tag.name})

        await inter.send(f'Successfully deleted tag `{tag_name}`')

    @tag_delete.autocomplete('tag_name')
    async def tag_delete_autocomp(self, inter: AppCmdInter, string: str):
        string = string.lower()
        tags = [tag.name for tag in await self.bot.db.find('tags')]
        return utils.finder(string, tags, lazy=False)[:25]

    @base_tag.sub_command(name='list')
    async def tag_list(
        self,
        inter: AppCmdInter,
        member: disnake.Member = commands.Param(default=lambda inter: inter.author)
    ):
        """See the list of all the tags that the member owns."""

        await self.check_channel(inter)

        entries = []
        for tag in await self.bot.db.find('tags'):
            if tag.owned_by == member.id:
                entries.append(tag.name)

        if len(entries) == 0:
            return await inter.send(f'`{member}` has no tags.', ephemeral=True)

        p = utils.SimplePages(inter, entries, per_page=7, entries_name='tags')
        p.embed.title = f'{member.display_name}\'s tags'

        await p.start()

    @base_tag.sub_command(name='all')
    async def tag_all(self, inter: AppCmdInter):
        """See a list of all the existing tags."""

        await self.check_channel(inter)

        p = utils.SimplePages(
            inter, [tag.name for tag in await self.bot.db.find('tags')],
            per_page=7, entries_name='tags'
        )
        await p.start()

    @base_tag.sub_command(name='info')
    async def tag_info(
        self,
        inter: AppCmdInter,
        tag_name: str = commands.Param(
            description='The name of the tag to show info about'
        )
    ):
        """Shows info about a tag."""

        await self.check_channel(inter)

        tag_name = tag_name.lower()
        tag: Tags = await self.bot.db.find_one('tags', {'name': tag_name})
        if tag is None:
            return await inter.send(f'Tag `{tag_name}` not found.', ephemeral=True)

        em = disnake.Embed(color=utils.blurple)
        em.add_field(name='Tag Name', value=tag.name)

        usr = self.bot.get_guild(1097610034701144144).get_member(tag.owned_by)
        em.add_field(name='Owned By', value=f'{utils.format_name(usr)}')

        em.add_field(name='Uses', value=f'{tag.uses:,}', inline=False)

        em.add_field(
            name='Creation Date',
            value=f'{utils.format_dt(tag.created_at, "F")} '
                  f'`({utils.human_timedelta(tag.created_at, accuracy=5)})`',
            inline=False
        )
        em.set_footer(text=f'Requested By: {utils.format_name(inter.author)}')

        await inter.send(embed=em)

    @tag_info.autocomplete('tag_name')
    async def tag_info_autocomp(self, inter: AppCmdInter, string: str):
        string = string.lower()
        tags = [tag.name for tag in await self.bot.db.find('tags')]
        return utils.finder(string, tags, lazy=False)[:25]

    @commands.Cog.listener('on_message')
    async def check_for_tag_in_message(self, message: disnake.Message):
        if not message.author.bot and message.guild:
            if message.content.startswith('.'):
                filtered = message.content[1:].lower()
                for tag in await self.bot.db.find('tags'):
                    if filtered == tag.name:
                        em = disnake.Embed()
                        if tag.attachment != 'None':
                            em.set_image(tag.attachment)
                        if tag.content != 'None':
                            em.description = tag.content

                        await message.channel.send(embed=em)
                        tag.uses += 1
                        await tag.commit()
                        break

    @commands.Cog.listener('on_member_remove')
    async def del_all_user_tags_on_leave(self, member: disnake.Member):
        if member.guild.id == 1097610034701144144:
            await self.bot.db.delete('tags', {'owned_by': member.id})


def setup(bot: Astemia):
    bot.add_cog(_Tags(bot))
