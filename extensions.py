from au.meta.logs import get_logger; log = get_logger(__name__)

import os
import traceback
import paths
from enum import Enum

class ReloadState(Enum):
    reloaded = 'Modified'
    loaded = 'Loaded'
    unloaded = 'Unloaded'
    recovered = 'Recovered'
    failed_recover = 'Failed_recover'
    failed = 'Failed'
    unchanged = 'Unchanged'
    
MISSING = object()


class ExtensionWrap:
    def __init__(self, bot, path) -> None:
        self.bot = bot
        
        self.loaded_module = None
        self.last_modified = None
        self.last_reload_state = ReloadState.unchanged
        
        self.path = path
        root, file = self.path.rsplit(os.sep, 1)
        
        self.lib_name = self.path.replace(os.sep,'.').rsplit('.',1)[0]
        self.name = self.lib_name
        
        self.backup_folder = os.path.join(paths.storage, 'reload', root)
        self.backup_path = os.path.join(self.backup_folder, file)
        self.backup_lib_name = self.backup_path.replace(os.sep,'.').rsplit('.',1)[0]
        
        
    def check_modified(self):
        if not os.path.isfile(self.path):
            log.warning(f'File not found: {self.path}')
            return MISSING
        
        return os.stat(self.path).st_mtime
    
    
    def backup(self):
        with open(self.path, "r", encoding="utf-8") as f:
            os.makedirs(self.backup_folder, exist_ok=True)
            
            with open(self.backup_path, "w", encoding="utf-8") as w:
                w.write(f.read())
        
        
    def mark_ready(self, module):
        self.last_modified = self.check_modified()
        self.loaded_module = module
        
        
    async def reload(self):
        did_unload = False
        last = self.last_modified
        current = self.check_modified()
            
        if last == current:
            return ReloadState.unchanged

        if self.loaded_module:
            did_unload = True
            try:
                await self.bot.unload_extension(self.loaded_module)
                log.debug(f'unloaded extension: {self.loaded_module}')
                self.loaded_module = None
            except Exception:
                pass
        
        if current is MISSING:
            return ReloadState.unloaded
            
        try:
            await self.bot.load_extension(self.lib_name)
            self.mark_ready(self.lib_name)
            self.backup()
            log.debug(f'Loaded extension: {self.lib_name}')
            
            if did_unload:
                return ReloadState.reloaded

            return ReloadState.loaded
            
            
        except Exception as e:
            traceback.print_exc()
            log.warning(f'Failed to load extension: {self.lib_name}')
            
            # Should only check tmp if successfully loaded this run.
            if (self.loaded_module or did_unload) and os.path.isfile(self.backup_path):
                try:
                    await self.bot.load_extension(self.backup_lib_name)
                    self.mark_ready(self.backup_lib_name)
                    log.info(f'Reverting to last working: {self.backup_lib_name}')
                    return ReloadState.recovered
                    
                except Exception:
                    return ReloadState.failed_recover
                
        return ReloadState.failed
        