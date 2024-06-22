from flask import Flask, request,g
from gingerjs.app import App
import os
from flask_cors import CORS
from gingerjs import add_url_rules

app = App(__name__, template_folder='build/templates',static_url_path='/static',static_folder='public/static/')
CORS(app,resources={r"/api/*": {"origins": "*"}})

@app.before_request
def before_request():
    # When you import jinja2 macros, they get cached which is annoying for local
    # development, so wipe the cache every request.
    if os.environ.get('DEBUG') == "True" or False:
        app.jinja_env.cache = {}

# Generate Flask routes
add_url_rules(os.path.join(os.getcwd(),"src","app"),app,debug=True if os.environ.get('DEBUG')=="True" else False)

if __name__ == '__main__':
    debug_app = os.environ.get('DEBUG')
    app.run_app(debug=debug_app,host=os.environ.get('HOST'),port=os.environ.get('PORT'))