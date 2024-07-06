import os
import importlib.util

# Load settings from settings.py if available
def load_settings():
    settings = {
        'NAME': 'GingerJs',
        'VERSION': '1.0',
        'PACKAGE_MANAGER': 'npm',
        'DEBUG': True,
        "PORT": 5001,
        "HOST": "0.0.0.0",
        "PYTHONDONTWRITEBYTECODE" : ""
    }
    settings_path = os.path.join(os.getcwd(), 'settings.py')
    if os.path.exists(settings_path):
        spec = importlib.util.spec_from_file_location("settings", settings_path)
        settings_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(settings_module)
        settings.update({key: getattr(settings_module, key) for key in dir(settings_module) if not key.startswith("__")})
    return settings