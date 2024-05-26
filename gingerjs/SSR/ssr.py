from flask import render_template
import os
import subprocess
import json

frontend_dir = 'build'
app_dir = "app"
ext = "js"

def set_default_props(req,props):
    props['location']["path"] = req.path
    # props['location']['baseUrl'] = req.base_url
    props['location']['query'] = str(req.query_string,"utf-8")
    return props

def ssr(req,props={}):
    props["location"] = {}
    if("favicon" in req.path):
        return ""
    props = set_default_props(req,props)
    renderRoute = ['node', f"{os.path.dirname(os.path.abspath(__file__))}/routes.js" ,json.dumps(props)]
    data =  subprocess.check_output(renderRoute)
    return render_template("index.html",react_context=str(data,'utf-8'),react_props=props)
