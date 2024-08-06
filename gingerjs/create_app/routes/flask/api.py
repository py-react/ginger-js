from fastapi import Request
from functools import wraps

def api(module):
    @wraps(module)
    async def api_func(*args, **kwargs):
        return await module(*args, **kwargs)
    return api_func