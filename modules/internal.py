from au.meta.logs import get_logger; log = get_logger(__name__)
from discord.ext import commands
import checks
from extensions import ReloadState

emojis = {
    ReloadState.loaded:'✅',
    ReloadState.reloaded:'✅',
    ReloadState.failed:'❌',
    ReloadState.failed_recover:'‼️',
    ReloadState.recovered:'⚠️',
}


class CogInternal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='reload', aliases=['rl'], hidden=True)
    @checks.is_owner()
    async def _reload(self, ctx):
        """Reloads all modules."""
        items = await self.bot.reload_cogs()
        
        display = []
        for i in items:
            if i.last_reload_state not in emojis:
                continue
            
            emoji = emojis.get(i.last_reload_state)
            display.append(f'{emoji}`{i.name}`')
        
        if not display:
            return await ctx.send('Up to date')
        
        await ctx.send('\n'.join(display))
        
        
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        await ctx.reply(f':warning: {error}')


async def setup(bot):
    await bot.add_cog(CogInternal(bot))
