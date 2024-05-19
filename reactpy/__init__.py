import os
import importlib.util

def add_url_rules(root_folder,server):
    for dirpath, _, filenames in os.walk(root_folder):
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
                # Assume the module has a `view_func` function
                if hasattr(module, 'index'):
                    server.add_url_rule(url_rule, endpoint=url_rule, view_func=module.index)
                else:
                    print(f"No 'view_func' found in {relative_path}")
