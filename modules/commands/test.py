from au.meta.logs import get_logger; log = get_logger(__name__)
from discord.ext import commands
import checks

class CogTest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def test(self, ctx):
        await ctx.send('test passed')


async def setup(bot):
    await bot.add_cog(CogTest(bot))
