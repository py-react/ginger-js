import os
import importlib.util
from .api import api
from .view import view


def define_routes(app,root_folder,func_type,bridge):
    for dirpath, _, filenames in os.walk(root_folder):
        if ("/api/" not in dirpath and func_type == "view") or (func_type == "api"):
            for filename in filenames:
                if filename == 'index.py':
                    # Construct relative path from 'src'
                    relative_path = os.path.relpath(os.path.join(dirpath, filename), root_folder)
                    # Create a URL rule for Flask
                    url_rule = '/' + os.path.dirname(relative_path).replace(os.sep, '/')
                    # Replace placeholders with Flask route variables
                    url_rule = url_rule.replace('[', '<').replace(']', '>')
                    if url_rule == '/.':  # Root index.py
                        url_rule = '/'
                    else:
                        url_rule = url_rule + '/'
                    # Dynamic import of the module
                    module_name = relative_path.replace(os.sep, '.')[:-3]  # Convert path to module name
                    spec = importlib.util.spec_from_file_location(module_name, os.path.join(dirpath, filename))
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    if hasattr(module, 'index'):
                        if func_type == "api":
                            app.add_url_rule(f"/api{url_rule}", endpoint=f"/api{url_rule}", view_func=api(module))
                        elif func_type == "view":
                            app.add_url_rule(url_rule, endpoint=url_rule, view_func=view(module,bridge))
                    else:
                        print(f"No 'view_func' found in {relative_path}")