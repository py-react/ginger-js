import os
from contextlib import asynccontextmanager
from gingerjs.app import App
from fastapi import FastAPI
from gingerjs.create_app.load_settings import load_settings
import subprocess
import psutil

LOCKFILE = "/tmp/my_subprocess.lock"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load
    if not os.path.exists(LOCKFILE):
        settings = load_settings()
        subprocess.run(["yarn" if settings.get("package_manager","npm") == "yarn" else "npm","run","generate-client"])
    yield
    if os.path.exists(LOCKFILE):
        with open(LOCKFILE) as f:
            pid = int(f.read())
            process = psutil.Process(pid)
            if process:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
            if os.path.exists(LOCKFILE):
                os.remove(LOCKFILE)
    # Clean up and release the resources
    pass

app = App(__name__,lifespan=lifespan)