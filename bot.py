import discord
from discord.ext import commands
import aiohttp
import asyncio
import os
import logging
import config
import paths

from extensions import ExtensionWrap, ReloadState

# logger = logging.getLogger('discord')
# logger.setLevel(logging.DEBUG)

# TODO https://stackoverflow.com/questions/6729268/log-messages-appearing-twice-with-python-logging
# Remove handler from discord logger to stop double logs.

logging.basicConfig(format='[{asctime}] [{levelname:<8}] {name}: {message}',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    style='{',
                    level=logging.DEBUG)
log = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True


class DiscordBot(commands.bot.BotBase, discord.AutoShardedClient):
    
    def __init__(self):
        self.config = config
        self.paths = paths
        
        self.is_loaded = False
        self.loaded_extensions = {}
        self.session = None
        
        super().__init__(command_prefix='.', case_insensitive=True, help_attrs=dict(hidden=True), intents=intents)
        self.loop = asyncio.get_event_loop()


    async def reload_cogs(self, cog_fps:list[str]=None, loaded=True) -> dict[ReloadState, list[ExtensionWrap]]:
        '''
        cog_fps - which files to reload
        loaded - reload all loaded cogs (this unloads files that have been deleted)
        
        ---
        Ignores folders starting with _
        Like /__pycache__
        
        Ignore files starting with _
        Ignores non .py files.
        '''
        cog_fps = cog_fps or []
        outputs = []

        if not cog_fps:
            # find files to load
            for root, _, files in os.walk(paths.modules):
                last_folder_name = root.split(os.sep,1)[-1]
                if last_folder_name.startswith('_'):
                    continue
                
                for file in files:
                    fp = os.path.join(root,file)
                    file_name, ext = file.rsplit('.',1)
                    if not ext in ['py']:
                        continue
                    
                    if '.py.' in file_name: # For .py.tmp
                        continue
                    
                    if file_name.startswith('_'):
                        continue
                    
                    cog_fps.append(fp)
                    
                    
        if loaded:
            for k in self.loaded_extensions.keys():
                if not k in cog_fps:
                    cog_fps.append(k)
                
                
        for fp in cog_fps:
            extension = self.loaded_extensions.get(fp)
            if not extension:
                extension = ExtensionWrap(self, fp)
                self.loaded_extensions[fp] = extension
            
            extension.last_reload_state = await extension.reload()
            outputs.append(extension)
            
        return outputs


    async def on_ready(self):
        await self.reload_cogs()
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.is_loaded = True
        log.info('Ready')


    async def close(self):
        await super().close()
        await self.session.close() # Close open aiohttp session.


def run_bot():
    bot = DiscordBot()
    bot.run(config.token, reconnect=True)


run_bot()