import os
from flask import request,render_template
from gingerjs.SSR import ssr,partial_ssr

def view(module,bridge):
    def view_func(**kwargs):
        if("favicon" in request.path):
            return ""
        props = None
        layout_props = {}
        if hasattr(request,"prop_data"):
            layout_props = request.prop_data
            delattr(request,"prop_data")
        # so actual controller of the view will not get this extra attr
        kwargs.setdefault("request", request)
        if len(tuple(kwargs.values())):
            props = module.index(**kwargs)
        else:
            props = module.index()

        if props == None:
            props = {}

        if layout_props == None:
            layout_props = {}
        props["location"] = {}
        props["layout_props"] = layout_props
        
        props['location']["path"] = request.path
        # props['location']['baseUrl'] = req.base_url
        props['location']['query'] = str(request.query_string,"utf-8")
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            toRender = partial_ssr(bridge,props)
        else:
            toRender = ssr(bridge,props)
        if os.environ.get('DEBUG', "False") == "True":
            if ("<template data-stck=" in toRender) or ("<template data-msg=" in toRender):
                props["hasError"] = "true"
                props["error"] = toRender
                toRender = ssr(bridge,props)
        meta = {
            "title": "GingerJs"
        }
        if hasattr(module, 'meta_data'):
            meta = module.meta_data()
        return render_template("index.html",react_context=toRender,react_props=props,meta_info=meta)
    return view_func