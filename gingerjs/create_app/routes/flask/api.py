from fastapi import Request

def api(module):
    async def api_func(request:Request):
        return await module(request)
    return api_func