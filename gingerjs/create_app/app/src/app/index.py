from fastapi import Request
async def meta_data():
    return {
        "title": "Ginger-Js",
    }


async def index(request:Request):
    isDev = "true"
    return {"isdev":isDev}