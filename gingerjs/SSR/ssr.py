import json

def ssr(bridge,props={}):
    return bridge.send_and_receive(json.dumps({"type":"ssr","data":props}))
