import json
from werkzeug.exceptions import NotFound

def ssr(bridge,props={}):
    if ".js.map" in str(props["location"]["path"]):
        NotFound()
        return
    return bridge.send_and_receive(json.dumps({"type":"ssr","data":props}))

def partial_ssr(bridge,props={}):
    if ".js.map" in str(props["location"]["path"]):
        NotFound()
        return
    props["suppressHydrationWarning"] = "true"
    return bridge.send_and_receive(json.dumps({"type":"partial_ssr","data":props}))