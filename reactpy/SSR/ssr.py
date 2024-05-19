from flask import render_template
import os
import subprocess
import json

frontend_dir = 'build'
app_dir = "app"
ext = "js"

def set_default_props(req,props):
    props['location']["path"] = req.path
    props['location']['baseUrl'] = req.base_url
    props['location']['query'] = str(req.query_string,"utf-8")
    return props

def ssr(req,props={"location":{}}):
    if("favicon" in req.path):
        return ""
    props = set_default_props(req,props)
    file_name = "index.jsx"
    if(req.path != "/"):
        file_name = f"{req.path[1:]}/index.{ext}"
    file_path = os.path.join(os.getcwd(), frontend_dir, app_dir, file_name)
    renderRoute = ['node', "routes.js", file_path ,json.dumps(props)]
    data =  subprocess.check_output(renderRoute)
    return render_template("index.html",react_context=str(data,'utf-8'),react_props=json.dumps(props))
