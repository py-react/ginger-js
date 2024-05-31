from flask import request,jsonify

def api(module):
    def api_func(**kwargs):
        data = None
        kwargs.setdefault("request", request)
        if len(tuple(kwargs.values())):
            data = module.index(**kwargs)
        else:
            data = module.index(**kwargs)
        if data == None:
            data = {"Error":"No Data"}
        return jsonify(data)
    return api_func