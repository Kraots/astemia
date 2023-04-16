import time
import psutil

import disnake
from disnake.ext import commands

import utils
from utils import Context

from main import Astemia


class Misc(commands.Cog):
    """Miscellaneous commands, basically commands that i have no fucking idea where to fucking put so they just come in this category."""
    def __init__(self, bot: Astemia):
        self.bot = bot

    @property
    def display_emoji(self) -> str:
        return '🔧'

    @commands.command()
    async def ping(self, ctx: Context):
        """See the bot's ping.
        **NOTE:** This command can only be used in <#1078234687153131554>
        """

        ping = disnake.Embed(title="Pong!", description="_Pinging..._", color=utils.red)
        start = time.time() * 1000
        msg = await ctx.better_reply(embed=ping)
        end = time.time() * 1000
        ping = disnake.Embed(
            title="Pong!",
            description=f"Websocket Latency: `{(round(self.bot.latency * 1000, 2))}ms`"
            f"\nBot Latency: `{int(round(end-start, 0))}ms`"
            f"\nResponse Time: `{(msg.created_at - ctx.message.created_at).total_seconds()/1000}` ms",
            color=utils.red
        )
        ping.set_footer(text=f"Online for {utils.human_timedelta(dt=self.bot.uptime, suffix=False)}")
        await msg.edit(embed=ping)

    @commands.command()
    async def uptime(self, ctx: Context):
        """See how long the bot has been online for.
        **NOTE:** This command can only be used in <#1078234687153131554>
        """

        uptime = disnake.Embed(
            description=f"Bot has been online since {utils.format_dt(self.bot.uptime, 'F')} "
                        f"(`{utils.human_timedelta(dt=self.bot.uptime, suffix=False)}`)",
            color=utils.red
        )
        uptime.set_footer(text=f'Bot made by: {self.bot._owner}')
        await ctx.better_reply(embed=uptime)

    @commands.command(name='metrics')
    async def show_metrics(self, ctx: Context):
        """Shows the metrics as well as some info about the bot."""

        em = disnake.Embed(title='Metrics', description='_Fetching Metrics..._', colour=utils.invisible)
        start = time.time() * 1000
        msg = await ctx.better_reply(embed=em)
        end = time.time() * 1000

        process = psutil.Process()
        mem = process.memory_full_info()
        cpu_usage = psutil.cpu_percent()
        physical = utils.natural_size(mem.rss)
        threads = process.num_threads()
        pid = process.pid

        commands = 0
        for _ in self.bot.walk_commands():
            commands += 1

        extensions = len(self.bot.extensions)

        em = disnake.Embed(title='Metrics', colour=utils.invisible)
        em.add_field(
            name='Ping',
            value=f'Websocket Latency: `{(round(self.bot.latency * 1000, 2))}ms`'
                  f'\nBot Latency: `{int(round(end-start, 0))}ms`'
                  f'\nResponse Time: `{(msg.created_at - ctx.message.created_at).total_seconds()/1000}` ms',
            inline=False
        )
        em.add_field(
            name='Memory Usage',
            value=f'CPU: {cpu_usage}%'
                  f'\nRAM Usage: {physical}'
                  f'\nThreads: {threads}'
                  f'\nPID: {pid}',
            inline=False
        )
        em.add_field(
            name='Extras',
            value=f'Running on commit [``{self.bot.git_hash[:7]}``](https://github.com/Kraots/ukiyo/tree/{self.bot.git_hash})'
                  f'\nCommands: {commands}'
                  f'\nExtensions: {extensions}'
                  f'\nUptime: {utils.human_timedelta(dt=self.bot.uptime, suffix=False)}',
            inline=False
        )

        em.set_footer(
            text=f'Bot made by: {self.bot._owner}',
            icon_url=self.bot.user.display_avatar.url
        )

        await msg.edit(embed=em)

def setup(bot: Astemia):
    bot.add_cog(Misc(bot))
