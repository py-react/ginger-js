from fastapi import Request
async def GET(request:Request):
    return {"user":"1"}

async def POST(request:Request):
    return {"message":"done"}

async def PUT(request:Request):
    return {"message":"done"}

async def DELETE(request:Request):
    return {"message":"done"}