from flask import Flask, render_template, request, jsonify
import os
import subprocess
import importlib.util
import json
from flask_cors import CORS
from reactpy import add_url_rules


app = Flask(__name__, template_folder='public/templates',static_url_path='',static_folder='public/static/')
CORS(app,resources={r"/api/*": {"origins": "*"}})

# Generate Flask routes based on frontend folder structure
add_url_rules(os.path.join(os.getcwd(),"src","app"),app)

@app.before_request
def before_request():
    # When you import jinja2 macros, they get cached which is annoying for local
    # development, so wipe the cache every request.
    if 'localhost' in request.host_url or '0.0.0.0' in request.host_url:
        app.jinja_env.cache = {}

# app.add_url_rule("/counter",view_func=counter)
if __name__ == '__main__':
    
    app.run(debug=True,host="0.0.0.0")
