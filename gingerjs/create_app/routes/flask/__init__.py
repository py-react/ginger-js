import re
from collections import defaultdict
import os
import importlib.util
from .api import api
from .view import view
from .exception_view import exception
from .not_found import not_found
from .middleware import add_middleware
from .layout_view import layout_middleware





def define_routes(app,root_folder,route_type,bridge,*args, **kwargs):
    def debug_log (*a, **kwa):
        if kwargs.get("debug", False):
            print(f"{os.getpid()} App Route: " ,*a, **kwa)
    app.config['TRAP_HTTP_EXCEPTIONS']=True
    app.errorhandler(404)(not_found(bridge))
    app.errorhandler(Exception)(exception(bridge))
    routes_tree = []
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

                # Dynamic import of the layout module
                relative_path_layout = os.path.relpath(os.path.join(dirpath, "layout.py"), root_folder)
                layout_module_name = relative_path_layout.replace(os.sep, '.')[:-3]  # Convert path to module name
                layout_spec = importlib.util.spec_from_file_location(layout_module_name, os.path.join(dirpath, "layout.py"))
                layout_module = importlib.util.module_from_spec(layout_spec)

                if os.path.isfile(os.path.join(dirpath, "layout.py")):
                    layout_spec.loader.exec_module(layout_module)
                
                if os.path.isfile(os.path.join(dirpath, "middleware.py")):
                    middleware_spec.loader.exec_module(middleware_module)
                if root_folder == dirpath and filename == "middleware.py":
                    if hasattr(middleware_module, 'middleware',):
                        if route_type == "api":
                            add_middleware(app,f"/api{url_rule}",middleware_module.middleware)
                            routes_tree.append(f"Middleware attached on api '/api{url_rule}' attached it using middleware.py in {dirpath}")
                        elif route_type == "view":
                            add_middleware(app,url_rule,middleware_module.middleware)
                            routes_tree.append(f"Middleware attached on route '{url_rule}' attached it using middleware.py in {dirpath}")
                    else:
                        routes_tree.append(f"No 'middleware' found for '/api{url_rule}' attach it by adding middleware.py in {dirpath}")

                if root_folder == dirpath and filename == "layout.py" and route_type == "view":
                    if hasattr(middleware_module, 'layout',):
                        layout_middleware(app,url_rule,layout_module.layout)
                        routes_tree.append(f"layout attached on route '{url_rule}' attached it using layout.py in {dirpath}")
                    else:
                        routes_tree.append(f"No 'lauout' found for '{url_rule}' attach it by adding layout.py in {dirpath}")
                    
                if filename == 'index.py':
                    # Dynamic import of the module
                    module_name = relative_path.replace(os.sep, '.')[:-3]  # Convert path to module name
                    spec = importlib.util.spec_from_file_location(module_name, os.path.join(dirpath, filename))
                    module = importlib.util.module_from_spec(spec)

                    spec.loader.exec_module(module)
                    if hasattr(middleware_module, 'middleware'):
                        if route_type == "api" and dirpath!= root_folder: # its dirpath!= root_folder because its already done above
                            add_middleware(app,f"/api{url_rule}",middleware_module.middleware)
                            routes_tree.append(f"Middleware attached on api '/api{url_rule}' attached it using middleware.py in {dirpath}")
                        elif route_type == "view" and dirpath!= root_folder: # its dirpath!= root_folder because its already done above
                            add_middleware(app,url_rule,middleware_module.middleware)
                            routes_tree.append(f"Middleware attached on route '{url_rule}' attached it using middleware.py in {dirpath}")
                    else:
                        if route_type == "api":
                            routes_tree.append(f"No 'middleware' found for api '/api{url_rule}' attach it by adding middleware.py in {dirpath}")
                        elif route_type == "view":
                            routes_tree.append(f"No 'middleware' found for '{url_rule}' attach it by adding middleware.py in {dirpath}")

                    if hasattr(module, 'index'):
                        if route_type == "api":
                            app.add_url_rule(f"/api{url_rule}", endpoint=f"/api{url_rule}", view_func=api(module),methods=["GET","POST","PUT","DELETE","OPTIONS"])
                            routes_tree.append(f"API route '/api{url_rule}' attached it using index.py in {dirpath}")
                        elif route_type == "view":
                            app.add_url_rule(url_rule, endpoint=url_rule, view_func=view(module,bridge))
                            if hasattr(layout_module, 'layout'):
                                layout_middleware(app,url_rule,layout_module.layout)
                                routes_tree.append(f"layout attached on route '{url_rule}' attached it using layout.py in {dirpath}")
                            routes_tree.append(f"Route '{url_rule}' attached it using index.py in {dirpath}")

                    else:
                        debug_log(f"No 'view_func' found in {relative_path}")


    if os.environ.get("DEBUG", "Falase") == "True":
        # Define regex patterns to match routes and actions
        route_pattern = re.compile(r"Route '(.*?)' attached it using (.*?) in")
        no_middleware_pattern = re.compile(r"No 'middleware' found for '(.*?)' attach it by adding middleware.py in")
        middleware_pattern = re.compile(r"Middleware attached on route '(.*?)' attached it using middleware.py")
        layout_pattern = re.compile(r"layout attached on route '(.*?)' attached it using layout.py")

        api_pattern = re.compile(r"API route '(.*?)' attached")
        no_api_middleware_pattern = re.compile(r"No 'middleware' found for api '(.*?)' attach it by adding middleware.py in")
        api_middleware_pattern = re.compile(r"Middleware attached on api '(.*?)' attached it using middleware.py")

        # Parse the log entries to extract routes and their actions
        routes = defaultdict(list)

        for line in routes_tree:
            route_match = route_pattern.search(line)
            no_middleware_match = no_middleware_pattern.search(line)
            middleware_match = middleware_pattern.search(line)
            layout_match = layout_pattern.search(line)

            api_match = api_pattern.search(line)
            no_api_middleware_match = no_api_middleware_pattern.search(line)
            api_middleware_match = api_middleware_pattern.search(line)
            
            if route_match:
                route, action = route_match.groups()
                routes[route].append(f"Page {action}")
            elif no_middleware_match:
                route = no_middleware_match.group(1)
                routes[route].append("No 'middleware' found")
            elif middleware_match:
                route = middleware_match.group(1)
                routes[route].append("Middleware attached on this route and subroutes")
            elif layout_match:
                route = layout_match.group(1)
                routes[route].append("Layout attached using layout.py")
            elif api_match:
                route = api_match.group(1)
                routes[route].append("Api Endpoint")
            elif no_api_middleware_match:
                route = no_api_middleware_match.group(1)
                routes[route].append("No 'middleware' found")
            elif api_middleware_match:
                route = api_middleware_match.group(1)
                routes[route].append("middleware.py")

        # Function to print the tree structure
        def print_tree(routes,route_type):
            def print_branch(route, indent=""):
                debug_log(indent + route)
                indent += "    "
                for action in routes[route]:
                    debug_log(indent + "|-- " + action)
                for subroute in sorted(routes.keys()):
                    if subroute != route and subroute.startswith(route) and subroute[len(route)] == '/':
                        print_branch(subroute, indent)

            root_routes = [route for route in routes.keys() if route.count('/' if route_type == "view" else "/api") == 1]
            for root in sorted(root_routes):
                print_branch(root)

        # Print the tree structure
        debug_log("")
        debug_log("R̲o̲u̲t̲e: ",route_type)
        debug_log("")
        print_tree(routes,route_type)    