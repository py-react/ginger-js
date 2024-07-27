import os
from gingerjs.SSR import ssr,partial_ssr
from fastapi import  Request
from fastapi.responses import  Response

async def static_route_func():
    return {}


def view(module,bridge,app,static_route=False):
    async def view_func(request: Request):
        if request.url.path.endswith(".ico") or request.url.path.endswith(".js.map") or request.url.path.endswith(".js") or request.url.path.endswith(".css"):
            raise Response(status_code=404)
        
        props = None
        layout_props = {}
        if hasattr(request.state,"prop_data"):
            layout_props = request.state.prop_data
            delattr(request.state,"prop_data")
        # so actual controller of the view will not get this extra attr
        if not static_route:
            props = await module.index(request)
        elif static_route:
            props = await static_route_func()

        if props == None:
            props = {}

        if layout_props == None:
            layout_props = {}
        props["location"] = {}
        props["layout_props"] = layout_props
        
        props['location']["path"] = request.url.path
        # props['location']['baseUrl'] = req.base_url
        props['location']['query'] = request.url.query
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            toRender = partial_ssr(bridge,props)
        else:
            toRender = ssr(bridge,props)
        if os.environ.get('DEBUG', "False") == "True":
            # TODO: check the below, is it still a valid case.
            if ("<template data-stck=" in toRender) or ("<template data-msg=" in toRender):
                props["hasError"] = "true"
                props["error"] = toRender
                toRender = ssr(bridge,props)
        meta = {
            "title": "GingerJs"
        }
        if hasattr(module, 'meta_data'):
            meta = await module.meta_data()

        return app.TemplateResponse(request=request,name="index.html",context={"react_context":toRender,"react_props":props,"meta_info":meta},status_code=200)
    return view_func