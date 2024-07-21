from gingerjs.SSR import ssr
from fastapi.responses import Response

def not_found(bridge,app):
    def view_func(request,*args,**kwargs):
        if request.url.path.endswith(".ico") or request.url.path.endswith(".js.map") or request.url.path.endswith(".js") or request.url.path.endswith(".css"):
            return Response(status_code=404)
        props = {}
        props["location"] = {}
        props['location']["path"] = request.url.path
        props['location']['query'] = request.url.query
        toRender = ssr(bridge,props)
        meta = {
            "title": request.url.path+"?"+request.url.query
        }
        return app.TemplateResponse(name="not_found.html",request=request,context={"react_context":toRender,"react_props":props,"meta_info":meta,"not_found":True},status_code=404)
        # return render_template_string(not_found_template,error=True),404
    return view_func