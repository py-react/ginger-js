from contextlib import asynccontextmanager
from gingerjs.app import App
from fastapi import FastAPI
from gingerjs.create_app.load_settings import load_settings
import subprocess


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load
    settings = load_settings()
    subprocess.run(["yarn" if settings.get("package_manager","npm") == "yarn" else "npm","run","generate-client"])
    yield
    # Clean up and release the resources
    pass

app = App(__name__,lifespan=lifespan)




