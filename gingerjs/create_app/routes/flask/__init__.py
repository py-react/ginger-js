import os
import importlib.util
from .api import api
from .view import view
from .middleware import add_middleware




def define_routes(app,root_folder,route_type,bridge,*args, **kwargs):
    def debug_log (*a, **kwa):
        if kwargs.get("debug", False):
            print("App Route: " ,*a, **kwa)
    debug_log(f"############## Creating {route_type} ##############")
    for dirpath, _, filenames in os.walk(root_folder):
        if ("/api/" not in dirpath and route_type == "view") or (route_type == "api"):
            for filename in filenames:
                # Construct relative path from 'src'
                relative_path = os.path.relpath(os.path.join(dirpath, filename), root_folder)
                # Create a URL rule for Flask
                url_rule = '/' + os.path.dirname(relative_path).replace(os.sep, '/')
                # Replace placeholders with Flask route variables
                url_rule = url_rule.replace('[', '<').replace(']', '>')
                if url_rule == '/.':  # Root index.py
                    url_rule = '/'
                
                # Dynamic import of the middleware module
                relative_path_middelware = os.path.relpath(os.path.join(dirpath, "middleware.py"), root_folder)
                middleware_module_name = relative_path_middelware.replace(os.sep, '.')[:-3]  # Convert path to module name
                middleware_spec = importlib.util.spec_from_file_location(middleware_module_name, os.path.join(dirpath, "middleware.py"))
                middleware_module = importlib.util.module_from_spec(middleware_spec)
                
                if os.path.isfile(os.path.join(dirpath, "middleware.py")):
                    middleware_spec.loader.exec_module(middleware_module)
                if root_folder == dirpath and filename == "middleware.py":
                    if hasattr(middleware_module, 'middleware',):
                        if route_type == "api":
                            add_middleware(app,f"/api{url_rule}",middleware_module.middleware)
                            debug_log(f"Middleware attahced on route '/api{url_rule}' attached it using middleware.py in {dirpath}")
                        elif route_type == "view":
                            add_middleware(app,url_rule,middleware_module.middleware)
                            debug_log(f"Middleware attahced on route '{url_rule}' attached it using middleware.py in {dirpath}")
                    else:
                        debug_log(f"No 'middleware' found for '/api{url_rule}' attach it by adding middleware.py in {dirpath}")

                    
                if filename == 'index.py':
                    # Dynamic import of the module
                    module_name = relative_path.replace(os.sep, '.')[:-3]  # Convert path to module name
                    spec = importlib.util.spec_from_file_location(module_name, os.path.join(dirpath, filename))
                    module = importlib.util.module_from_spec(spec)

                    spec.loader.exec_module(module)
                    if hasattr(middleware_module, 'middleware'):
                        if route_type == "api" and dirpath!= root_folder: # its dirpath!= root_folder because its already done above
                            add_middleware(app,f"/api{url_rule}",middleware_module.middleware)
                            debug_log(f"Middleware attahced on route '/api{url_rule}' attached it using middleware.py in {dirpath}")
                        elif route_type == "view" and dirpath!= root_folder: # its dirpath!= root_folder because its already done above
                            add_middleware(app,url_rule,middleware_module.middleware)
                            debug_log(f"Middleware attahced on route '{url_rule}' attached it using middleware.py in {dirpath}")
                    else:
                        if route_type == "api":
                            debug_log(f"No 'middleware' found for '/api{url_rule}' attach it by adding middleware.py in {dirpath}")
                        elif route_type == "view":
                            debug_log(f"No 'middleware' found for '{url_rule}' attach it by adding middleware.py in {dirpath}")

                    if hasattr(module, 'index'):
                        if route_type == "api":
                            app.add_url_rule(f"/api{url_rule}", endpoint=f"/api{url_rule}", view_func=api(module))
                            debug_log(f"Route '/api{url_rule}' attached it using index.py in {dirpath}")
                        elif route_type == "view":
                            app.add_url_rule(url_rule, endpoint=url_rule, view_func=view(module,bridge))
                            debug_log(f"Route '{url_rule}' attached it using index.py in {dirpath}")

                    else:
                        debug_log(f"No 'view_func' found in {relative_path}")