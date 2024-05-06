from discord.ext import commands
import config


def is_owner():
    def predicate(ctx):
        if not config.owners:
            raise commands.core.CheckFailure('Owner list empty.')
            
        if not ctx.message.author.id in config.owners:
            raise commands.core.CheckFailure('Unauthorized to run command.')
        
        return True
    return commands.check(predicate)