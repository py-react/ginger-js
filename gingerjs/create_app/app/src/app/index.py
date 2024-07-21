async def meta_data():
    return {
        "title": "Ginger-Js",
    }


async def index(request):
    isDev = "true"
    return {"isdev":isDev}