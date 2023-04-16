from dotenv import load_dotenv
load_dotenv()

import os
import aiohttp
import datetime

from dulwich.repo import Repo

import disnake
from disnake.ext import commands

import utils
from utils.views.help_command import PaginatedHelpCommand

TOKEN = os.getenv('BOT_TOKEN')
TO_REPLACE = os.getenv('NAMETOREPLACE')


class Astemia(commands.Bot):
    def __init__(self):
        super().__init__(
            max_messages=100000,
            help_command=PaginatedHelpCommand(),
            command_prefix=('!', '?', '.',),
            strip_after_prefix=True,
            case_insensitive=True,
            intents=disnake.Intents.all(),
            allowed_mentions=disnake.AllowedMentions(
                roles=False, everyone=False, users=True
            ),
            test_guilds=[1095130822610268180]
        ) 

        self._owner_id = 745298049567424623

        self.added_views = False

        self.execs = {}
        r = Repo('.')
        self.git_hash = r.head().decode('utf-8')
        r.close()

        self.load_extension('jishaku')
        os.environ['JISHAKU_NO_DM_TRACEBACK'] = '1'
        os.environ['JISHAKU_FORCE_PAGINATOR'] = '1'
        os.environ['JISHAKU_EMBEDDED_JSK'] = '1'
        os.environ['JISHAKU_EMBEDDED_JSK_COLOR'] = 'red'

        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                self.load_extension(f'cogs.{filename[:-3]}')

        for filename in os.listdir('./reload_cogs'):
            if filename.endswith('.py'):
                self.load_extension(f'reload_cogs.{filename[:-3]}')

    @property
    def _owner(self) -> disnake.User:
        if self._owner_id:
            return self.get_user(self._owner_id)

    @property
    def session(self) -> aiohttp.ClientSession:
        return self._session

    async def on_ready(self):
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()

        if not hasattr(self, '_session'):
            self._session = aiohttp.ClientSession(loop=self.loop)

        if not hasattr(self, '_presence_changed'):
            activity = disnake.Activity(type=disnake.ActivityType.watching, name='you | !help')
            await self.change_presence(status=disnake.Status.streaming, activity=activity)
            self._presence_changed = True

        if self.added_views is False:
            self.add_view(utils.AgeButtonRoles(), message_id=1095657274292310056)
            self.added_views = True

    async def process_commands(self, message):
        ctx = await self.get_context(message)
        await self.invoke(ctx)

    async def get_context(self, message, *, cls=utils.Context):
        return await super().get_context(message, cls=cls)


Astemia().run(TOKEN)
