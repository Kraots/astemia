import disnake
from disnake.ext import commands

from dulwich.repo import Repo

import utils
from utils import Context

from main import Astemia


class Github(commands.Cog):
    """Commands related to github."""
    def __init__(self, bot: Astemia):
        self.bot = bot
        self.github_client = utils.GithubClient(bot)

    @commands.group(
        name='github',
        aliases=('gh', 'git'),
        hidden=True,
        invoke_without_command=True,
        case_insensitive=True)
    async def base_github(self, ctx: Context):
        """Base github command."""

        await ctx.send_help('github')

    @base_github.command(name='source', aliases=('src',))
    async def github_source(self, ctx: Context, *, command: str = None):
        """Get the source on github for a command the bot has.
        `command` **->** The command you want to see. Can either be a prefixed command or a slash command.
        **NOTE:** This command can only be used in <#1078234687153131554>
        """

        if await ctx.check_channel() is False:
            return

        src = utils.GithubSource(self.bot.user.display_avatar)
        if command is not None:
            if command.lower() == 'help':
                pass
            elif command.lower().startswith(('jsk', 'jishaku')):
                url = 'https://github.com/Kraots/jishaku'
                return await ctx.reply(f'Sorry! That is a module\'s command. Here\'s the link to its github repo:\n<{url}>')
            else:
                command = self.bot.get_command(command) or self.bot.get_slash_command(command)
        data = await src.get_source(command)
        await ctx.better_reply(embed=data.embed, view=data.view)

    @base_github.command(name='user', aliases=('usr',))
    async def github_user(self, ctx: Context, *, username: str):
        """Search for a github user's account via its username.
        `username` **->** The user's github name.
        **NOTE:** This command can only be used in <#1078234687153131554>
        """

        if await ctx.check_channel() is False:
            return

        em = await self.github_client.get_user_info(username)
        await ctx.better_reply(embed=em)

    @base_github.command(name='repository', aliases=('repo',))
    async def github_repo(self, ctx: Context, *, repo: str):
        """Search for a github repository via the following format: `RepoOwnerUsername/RepoName`
        `repo` **->** The repo to search for.
        **NOTE:** This command can only be used in <#1078234687153131554>
        """

        if await ctx.check_channel() is False:
            return

        em = await self.github_client.get_repo_info(repo)
        await ctx.better_reply(embed=em)

    @base_github.command(name='pull')
    @utils.is_owner(owner_only=True)
    async def github_pull(self, ctx: Context):
        """Pulls the changes from the repo."""

        with ShellReader('git pull') as reader:
            content = "```" + reader.highlight
            content += f'\n{reader.ps1} git pull\n\n```'

            em = disnake.Embed(description=content)
            m = await ctx.send(embed=em)

            async for line in reader:
                content = content[:-3]
                content += line + '\n```'
                em.description = content
                await m.edit(embed=em)
        content = content[:-3]
        content += '\n[status] Git pull complete.\n```'
        em.description = content

        r = Repo('.')
        self.bot.git_hash = r.head().decode('utf-8')
        r.close()

        await m.edit(embed=em)

def setup(bot: Astemia):
    bot.add_cog(Github(bot))
