from flask import Flask, request,g
import os
from flask_cors import CORS
from gingerjs import add_url_rules


app = Flask(__name__, template_folder='public/templates',static_url_path='',static_folder='public/static/')
CORS(app,resources={r"/api/*": {"origins": "*"}})

@app.before_request
def before_request():
    # When you import jinja2 macros, they get cached which is annoying for local
    # development, so wipe the cache every request.
    if 'localhost' in request.host_url or '0.0.0.0' in request.host_url:
        app.jinja_env.cache = {}

# Generate Flask routes
add_url_rules(os.path.join(os.getcwd(),"src","app"),app,debug=False)

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port=os.environ.get('ENV_PORT', 5001))