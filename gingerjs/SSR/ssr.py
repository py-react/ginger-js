import json

def ssr(bridge,props={}):
    return bridge.send_and_receive(json.dumps({"type":"ssr","data":props}))

def partial_ssr(bridge,props={}):
    props["suppressHydrationWarning"] = "true"
    return bridge.send_and_receive(json.dumps({"type":"partial_ssr","data":props}))