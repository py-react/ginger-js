from os import environ,path,getcwd
from fastapi import FastAPI, HTTPException
from fastapi.templating import Jinja2Templates
from gingerjs.create_app.load_settings import load_settings
from fastapi.routing import APIRoute
from fastapi.responses import FileResponse
from gingerjs import add_url_rules
import importlib.util
from pathlib import Path
import json
import asyncio

def load_module(module_name,module_path):
    try:
        module_name = module_name
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        raise e

def app_context(request):
    return {'app': request.app}

class App(FastAPI):
    def __init__(self,*args, **kwargs):
        super().__init__(**kwargs)
        self._settings = load_settings()
        self.my_env = environ.copy()
        self.template_folder= path.sep.join(["_gingerjs","build","templates"])
        self.root_path= path.join(getcwd(),"src","app")
        self.setTemplateEngine()
        self.setStaticPath()
        self.add_url()
        self.extend_app()
        self.generate_openapi_schema()

    def generate_openapi_schema(self):
        output_file = "./public/static/openapi.json"
        schema = self.openapi()
        output_path = Path(output_file)
        output_path.write_text(json.dumps(schema, indent=2))
        print(f"OpenAPI schema saved to {output_file}")

    def extend_app(self):
        working_dir = self._settings["CWD"]
        app_name = self._settings["NAME"]
        try:
            app_module_present = load_module("extend_app",path.join(working_dir,app_name,f"main.py"))
            if app_module_present:
                app_module_present.extend_app(self)
        except Exception as e:
            print(e)
    
    def add_url(self):
        # Generate Flask routes
        add_url_rules(self,debug=self._settings.get("DEBUG",False))
    
    def setStaticPath(self):
        self.static_url_path='/static'
        self.static_folder=path.sep.join(["_gingerjs","build","static"])
        static_app = FastAPI()

        async def serve_static_file(file_path: str)->FileResponse:
            file_path_full = path.join(getcwd(),self.static_folder, file_path)
            # Check if the file exists
            if not path.isfile(file_path_full):
                raise HTTPException(status_code=404, detail="File not found")
            # Serve the file
            return FileResponse(file_path_full)
        
        route =APIRoute(
            path="/static/{file_path:path}",
            endpoint=serve_static_file,
            methods=["GET"],
            response_class=FileResponse,
            name="static"
        )
        static_app.router.routes.append(route)
        self.mount(self.static_url_path,app=static_app, name="static")
    
    def setTemplateEngine(self):
        
        self.templateEngine = Jinja2Templates(directory = self.template_folder,env=self._settings,auto_reload=True,autoescape=False, context_processors=[app_context])
        self.TemplateResponse = self.templateEngine.TemplateResponse
        