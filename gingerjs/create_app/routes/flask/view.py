from flask import request,render_template
from gingerjs.SSR import ssr

def view(module,bridge):
    def view_func(**kwargs):
        if("favicon" in request.path):
            return ""
        props = None
        kwargs.setdefault("request", request)
        if len(tuple(kwargs.values())):
            props = module.index(**kwargs)
        else:
            props = module.index()
        if props == None:
            props = {}
        props["location"] = {}
        props['location']["path"] = request.path
        # props['location']['baseUrl'] = req.base_url
        props['location']['query'] = str(request.query_string,"utf-8")
        toRender = ssr(bridge,props)
        return render_template("index.html",react_context=toRender,react_props=props)
    return view_func