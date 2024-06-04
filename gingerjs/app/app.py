import os
from flask import Flask


base = os.path.join(os.getcwd(),"src")

class App(Flask):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)

    def run_app(self, *args, **kwargs):
        print("Running app...")
        self.run(*args, **kwargs)




