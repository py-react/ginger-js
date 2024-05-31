from flask import request,abort

def add_middleware(app,endpoint,function):
        def middleware_func(*args, **kwargs):
            if request.path.startswith(endpoint):
                function(request,abort,*args, **kwargs)
        app.before_request(middleware_func)