import os
from gingerjs.create_app.load_settings import load_settings
class Logger():
    def __init__(self, name):
        self.settings = load_settings()
        self.name = name
    
    def debug(self, *args, **kwargs):
        if self.settings.get("DEBUG") or False:
            print(*args, **kwargs)
    
    def info(self, *args, **kwargs):
        print(*args, **kwargs)
    
    def error(self, *args, **kwargs):
        print(*args, **kwargs)