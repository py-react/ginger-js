import re
from collections import defaultdict
import os
import importlib.util
from .api import api
from .view import view
from .exception_view import exception
from .not_found import not_found
from .middleware import Create_Middleware_Class
from .layout_view import Create_Layout_Middleware_Class
from fastapi.routing import APIRoute
from fastapi.responses import HTMLResponse,JSONResponse
from fastapi import FastAPI
from starlette.exceptions import HTTPException as StarletteHTTPException
from gingerjs.create_app.load_settings import load_settings


def define_routes(app:FastAPI,root_folder,route_type,bridge,*args, **kwargs):
    def debug_log (*a, **kwa):
        if kwargs.get("debug", False):
            print(f"{os.getpid()} App Route: " ,*a, **kwa)
    settings = load_settings()
    app.add_exception_handler(404,not_found(bridge,app))
    app.add_exception_handler(StarletteHTTPException,exception(bridge,app))
    routes_tree = []
    for dirpath, _, filenames in os.walk(root_folder):
        if ("/api/" not in dirpath and route_type == "view") or (route_type == "api"):
            if settings.get("STATIC_SITE",False) and route_type != "api" and "index.py" not in filenames:
                # Construct relative path from 'src'
                relative_path = os.path.relpath(os.path.join(dirpath), root_folder)
                # Create a URL rule for Fast Api
                url_rule = '/' + os.path.dirname(relative_path).replace(os.sep, '/')
                # Replace placeholders with Fast Api route variables
                url_rule = url_rule.replace('[', '{').replace(']', '}')
                if url_rule == '/.':  # Root index.py
                    url_rule = '/'
                route =APIRoute(
                    path=url_rule,
                    endpoint=view(None,bridge,app,True),
                    methods=["GET"],
                    response_class=HTMLResponse,
                )
                app.router.routes.append(route)
                continue
            else:
                for filename in filenames:
                    # Construct relative path from 'src'
                    relative_path = os.path.relpath(os.path.join(dirpath, filename), root_folder)
                    # Create a URL rule for Fast Api
                    url_rule = '/' + os.path.dirname(relative_path).replace(os.sep, '/')
                    # Replace placeholders with Fast Api route variables
                    url_rule = url_rule.replace('[', '{').replace(']', '}')
                    if url_rule == '/.':  # Root index.py
                        url_rule = '/'


                    if filename == 'index.py':
                        # Dynamic import of the module
                        module_name = relative_path.replace(os.sep, '.')[:-3]  # Convert path to module name
                        spec = importlib.util.spec_from_file_location(module_name, os.path.join(dirpath, filename))
                        module = importlib.util.module_from_spec(spec)

                        spec.loader.exec_module(module)

                        if route_type == "api":
                            dependencies = []
                            if hasattr(module, 'middleware'):
                                # dependencies.append(Depends(module.middleware))
                                api_middleware_class =  Create_Middleware_Class(module.middleware,f"/api{url_rule}","api")
                                app.add_middleware(api_middleware_class)
                                routes_tree.append(f"Middleware attached on api '/api{url_rule}' attached it using middleware.py in {dirpath}")

                            methods = ["GET","POST","PUT","DELETE"]

                            for method in methods:
                                if hasattr(module, method):
                                    expectedParams = re.findall(r'\{(.*?)\}', f"/api{url_rule}")
                                    route = APIRoute(
                                        path=f"/api{url_rule}",
                                        endpoint=api(getattr(module, method)),
                                        methods=[method],
                                        response_class=JSONResponse,
                                        dependencies=dependencies
                                    )
                                    app.router.routes.append(route)

                            routes_tree.append(f"API route '/api{url_rule}' attached it using index.py in {dirpath}")
                        elif route_type == "view":
                            if hasattr(module, 'layout'):
                                layout_middleware_class =  Create_Layout_Middleware_Class(module.layout,url_rule)
                                app.add_middleware(layout_middleware_class)
                                routes_tree.append(f"layout attached on route '{url_rule}' attached it using layout.py in {dirpath}")
                            if hasattr(module, 'middleware'):
                                view_middleware_class =  Create_Middleware_Class(module.middleware,url_rule,"view")
                                app.add_middleware(view_middleware_class)
                                routes_tree.append(f"Middleware attached on route '{url_rule}' attached it using middleware.py in {dirpath}")
                            if hasattr(module, 'index'):
                                routes_tree.append(f"Route '{url_rule}' attached it using index.py in {dirpath}")
                                route =APIRoute(
                                    path=url_rule,
                                    endpoint=view(module,bridge,app),
                                    methods=["GET"],
                                    response_class=HTMLResponse,
                                )
                                app.router.routes.append(route)
                            elif settings.get("STATIC_SITE",False):
                                routes_tree.append(f"Route '{url_rule}' attached it using index.py in {dirpath}")
                                route =APIRoute(
                                    path=url_rule,
                                    endpoint=view(module,bridge,app,True),
                                    methods=["GET"],
                                    response_class=HTMLResponse,
                                )
                                app.router.routes.append(route)

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