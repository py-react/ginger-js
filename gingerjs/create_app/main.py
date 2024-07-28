
import click
import os
import subprocess
import shutil
import os
import signal
import sys
import time
from gingerjs.create_app.load_settings import load_settings
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import psutil
import importlib.util
from concurrent.futures import ThreadPoolExecutor


class Logger():
    def __init__(self, name):
        self.settings = load_settings()
        self.name = name
    
    def debug(self, *args, **kwargs):
        if self.settings.get("DEBUG") or False:
            print(*args, **kwargs)
    
    def info(self, *args, **kwargs):
        print(*args, **kwargs)
    
    def error(self, *args, **kwargs):
        print(*args, **kwargs)




observer = Observer()
dir_path = os.path.dirname(os.path.abspath(__file__))
logger = Logger("create gingerjs")

debug = os.environ.get("debug", "False") == "True" or False


def load_module(module_name,module_path):
    try:
        module_name = module_name
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        raise e


def find_process_by_port(port):
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            for conn in proc.connections(kind="tcp"):
                if str(conn.laddr.port) == str(port):
                    return proc
        except psutil.AccessDenied:
            continue
        except psutil.NoSuchProcess:
            continue
    return None

def kill_process(process):
    try:
        process.send_signal(signal.SIGTERM)
    except psutil.NoSuchProcess:
        pass

def run_command(cmd, env=None, cwd=None):
    print(f"Running command: {cmd}")
    process = subprocess.Popen(cmd, shell=True, env=env, cwd=cwd)
    process.wait()

def task_wrapper(func, name, *args, **kwargs):
    print(f"Starting task: {name}")
    return func(*args, **kwargs)

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, module,func_name,my_env,executor):
        self.executor = executor
        self.module = module
        self.settings = load_settings()
        self.func_name = func_name
        self.my_env = my_env
        for key, value in self.settings.items():
            self.my_env[key] = str(value)

    
    def debug_log(self, *args, **kwargs):
        if self.my_env["DEBUG"]:
            print(*args, **kwargs)

    def on_any_event(self, event):
        # Ignore events in __pycache__ directories
        if '__pycache__' in event.src_path or ".py" in event.src_path:
            return
        if event.is_directory:
            return
        self.debug_log(f"* Detected change in {event.src_path} ,reloading")
        self.restart(event.src_path)

    def restart(self,path):
        if hasattr(self.module, self.func_name):
            to_run = getattr(self.module, self.func_name)
            to_run(path)
            
        else:
            raise AttributeError("Module has no attribute "+self.func_name)


class Execution_time ():
    def __init__ (self,start_time,name):
        self.start_time = start_time
        self.name = name

    def end(self,end_time):
        execution_time = end_time - self.start_time
        print(f"{self.name} Done","Execution Time:", execution_time, "seconds")


# base = os.path.join(os.getcwd(),"example","app")
base = os.path.join(os.getcwd())

def create_dir(directory):
    # Ensure the directory exists
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except Exception as e:
        # show error
        print(e)

def create_and_write_file(directory, filename, content):
    # Ensure the directory exists
    try:
        create_dir(directory)
        # Full file path
        file_path = os.path.join(directory, filename)
        # Create and write to the file
        with open(file_path, 'w') as file:
            file.write(content)
    except Exception as e:
        # show error
        print(e)

def copy_file_if_not_exists(src, dst,copyFunc):
    if os.path.exists(dst):
        click.echo(f"The file {src} already exists. Operation skipped.")
    else:
        if os.path.exists(src):
            copyFunc(src, dst)
            click.echo(f"Copied {src} to {dst}.")
        else:
            click.echo(f"The file {src} doesn't exists. Operation skipped.")
            raise f"The file {src} doesn't exists"


@click.group()
def cli():
    pass

@cli.command()
def babel():
    """Builds the app using src folder (should be run after gingerjs cra)"""
    click.echo("Building babel app")
    settings = load_settings()
    package_manager = settings.get('PACKAGE_MANAGER')
    command = [
        'yarn' if package_manager== "yarn" else "npx" ,
        'babel',
        '--extensions', '.js,.jsx',
        './src',
        '-d', './_gingerjs/build'
    ]
    # Execute the command
    result = subprocess.run(command, capture_output=True, text=True,cwd=base)
    # Print the output
    if len(result.stderr):
        print("stderr:", result.stderr)
    else:
        print("stdout:", result.stdout)

@cli.command()
def build():
    """Builds the app using webpack config"""
    start_time = time.time()
    timing = Execution_time(start_time,"Building app")
    click.echo("Building app")
    my_env = os.environ.copy()
    node_process = None
    try:
        node_process=subprocess.run(["gingerjs","cra"], check=True,cwd=base,env=my_env)
    except  Exception as e:
        if node_process is not None:
            node_process.kill()
    end_time = time.time()
    timing.end(end_time)



@cli.command()
@click.argument('mode',required=False)
def dev_build(mode):
    """Builds the app in watch mode"""
    my_env = os.environ.copy()
    click.echo("Building app in in watch mode")
    settings = load_settings()
    package_manager = settings.get('PACKAGE_MANAGER')
    command = [
        'yarn' if package_manager == "yarn" else "npx",'nodemon',
        '--ext', 'jsx,tsx,js,json',
        '--watch', './src',
        '--watch', 'webpack.config.js',
        '--exec', 'gingerjs build'
    ]
    node_process = None
    try:
        node_process = subprocess.run(command,cwd=base,env=my_env)
    except  Exception as e:
        if node_process is not None:
            node_process.kill()

@cli.command()
def cra():
    """Creates a react app using src folder"""
    try:
        module_name = "create_app"
        module = load_module(module_name,os.path.join(dir_path,"create_app.py"))
        if hasattr(module, "create_app"):
            module.create_app()
    except Exception as e:
        raise e
        


@cli.command()
def create_app():
  """Intial project setup"""
  try:
    settings = load_settings()
    cwd = os.path.join(base)
    create_dir(cwd)
    copy_file_if_not_exists(os.path.join(dir_path,"app","settings.py"),os.path.join(cwd,"settings.py"),shutil.copy) # flask app
    click.echo("Setting up flask app")
    click.echo("flask app set complete")
    click.echo("Setting up app")
    copy_file_if_not_exists(os.path.join(dir_path,"app","package.json"),os.path.join(cwd,"package.json"),shutil.copy)
    copy_file_if_not_exists(os.path.join(dir_path,"app","postcss.config.js"),os.path.join(cwd,"postcss.config.js"),shutil.copy)
    copy_file_if_not_exists(os.path.join(dir_path,"app","tailwind.config.js"),os.path.join(cwd,"tailwind.config.js"),shutil.copy)
    copy_file_if_not_exists(os.path.join(dir_path,"app","jsconfig.json"),os.path.join(cwd,"jsconfig.json"),shutil.copy)
    copy_file_if_not_exists(os.path.join(dir_path,"app","components.json"),os.path.join(cwd,"components.json"),shutil.copy)
    copy_file_if_not_exists(os.path.join(dir_path,"app","public"),os.path.join(cwd,"public"),shutil.copytree)
    copy_file_if_not_exists(os.path.join(dir_path,"app","src"),os.path.join(cwd,"src"),shutil.copytree)
    create_dir(os.path.join(cwd,"public","static"))
    create_dir(os.path.join(cwd,"app","src","components"))
    click.echo("App set up completed")
    click.echo("Installing packages")
    package_manager = settings.get('PACKAGE_MANAGER')
    subprocess.run(["yarn" if package_manager == "yarn" else "npm", "install"], cwd=cwd)
    click.echo("Packages installed")
    click.echo("Run your app using : gingerjs runserver")
  except subprocess.CalledProcessError as e:
        click.echo(f"Error: {e}", err=True)

@cli.command()
@click.argument('mode',required=False)
def runserver(mode):
    """Runs the webapp"""
    try:
        settings = load_settings()
        my_env = os.environ.copy()  # Copy the current environment
        if mode == "dev":
            settings["DEBUG"] = True
            for key, value in settings.items():
                my_env[key] = str(value)
            click.echo("Building app in in watch mode")
            try:
                module_name = "create_app"
                module = load_module(module_name,os.path.join(dir_path,"create_app.py"))
                path = f".{os.path.sep}src"

                with ThreadPoolExecutor(max_workers=2) as executor:
                    if hasattr(module,"create_app"):
                        getattr(module, "create_app")()

                    event_handler = ChangeHandler(module, "build_changes", my_env, executor)
                    observer = Observer()

                    def start_observer():
                        observer.start()
                        observer.join()

                    observer.schedule(event_handler, path, recursive=True)
                    executor.submit(task_wrapper, start_observer,"File System Observer")
                    executor.submit(task_wrapper, run_command, "Run Uvicorn"," ".join(["uvicorn","_gingerjs.main:app","--reload","--port",settings.get("PORT"),"--host",settings.get("HOST")]), my_env, base)
                    # Keep the main thread alive to let the executor complete its tasks
                    try:
                        while True:
                            pass
                    except KeyboardInterrupt:
                        observer.stop()
                        executor.shutdown(wait=True)

            except  Exception as e:
                raise e
            return
        
        settings["DEBUG"] = False
        my_env["GINGERJS_APP_DIR"] = base
        for key, value in settings.items():
            my_env[key] = str(value)

        try:
            module_name = "create_app"
            module = load_module(module_name,os.path.join(dir_path,"create_app.py"))
            if hasattr(module, "create_app"):
                module.create_app()
            subprocess.run([f"uvicorn","_gingerjs.main:app","--port",settings.get("PORT"),"--host",settings.get("HOST")], check=True, cwd=base,env=my_env)
        except  Exception as e:
            raise e

    except Exception as e:
        click.echo(f"Error: {e}", err=True)

if __name__ == '__main__':
    cli()