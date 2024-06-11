from flask import request,abort

def layout_middleware(app,endpoint,func):
    def layout_func(*args, **kwargs):
        if request.path.startswith(endpoint):
            layoutData = func(request,*args, **kwargs)
            if hasattr(request,"prop_data"):
                request.prop_data[endpoint] = layoutData
            else:
                request.prop_data = {}
                request.prop_data[endpoint] = layoutData
    app.before_request(layout_func)