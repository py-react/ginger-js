
from reactpy.SSR.ssr import ssr
from flask import request
import requests


def index():
    api_url = 'https://dummyjson.com/products'  # Replace this with the URL of the API you want to fetch data from
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        return ssr(request,{"location":{},"products":data['products']})
    return ssr(request,{"location":{},"products":[]})
