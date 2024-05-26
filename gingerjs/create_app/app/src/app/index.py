from gingerjs.SSR.ssr import ssr
from flask import request

def index():
    return ssr(request)