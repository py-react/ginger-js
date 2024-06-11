import os
class Logger():
    def __init__(self, name):
        self.name = name
    
    def debug(self, *args, **kwargs):
        if os.environ.get("DEBUG") == "true" or False:
            print(*args, **kwargs)
    
    def info(self, *args, **kwargs):
        print(*args, **kwargs)
    
    def error(self, *args, **kwargs):
        print(*args, **kwargs)