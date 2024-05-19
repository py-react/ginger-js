
from reactpy.SSR.ssr import ssr
from flask import request


def index(productId):
    # api_url = f'https://dummyjson.com/products/{productId}'  # Replace this with the URL of the API you want to fetch data from
    # response = requests.get(api_url)

    # if response.status_code == 200:
    #     data = response.json()
    #     return ssr(request,{"location":{},"product":data})
    return ssr(request,{"location":{}})
