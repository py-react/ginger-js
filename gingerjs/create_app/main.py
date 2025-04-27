import re
import click
import os
import subprocess
import shutil
import signal
import time
from gingerjs.create_app.load_settings import load_settings
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import psutil
import importlib.util
from .user_input import main
import json
import multiprocessing



class Logger():
    def __init__(self, name):
        self.settings = load_settings()
        self.name = name
    
    def debug(self, *args, **kwargs):
        if self.settings.get("DEBUG") or False:
            print(f"{self.name}: ",*args, **kwargs)
    
    def info(self, *args, **kwargs):
        print(f"{self.name}: ",*args, **kwargs)
    
    def error(self, *args, **kwargs):
        print(f"{self.name}: ",*args, **kwargs)




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

def kill_process(process):
    try:
        process.send_signal(signal.SIGTERM)
    except psutil.NoSuchProcess:
        pass

def get_pids(port):
    returnItems = []
    command = "lsof -i :%s | awk '{print $2}'" % port
    pids = subprocess.check_output(command, shell=True)
    pids = pids.strip()
    if pids:
        pids = re.sub(' +', ' ', pids.decode("utf-8"))
        for pid in pids.split('\n'):
            try:
                returnItems.append(int(pid)) 
            except:
                pass
    return returnItems

def run_uvicorn():
    settings = load_settings()
    # Kill the uvicorn process if running on the same port
    port = int(settings.get("PORT", 5001))
    pid = get_pids(port)
    if len(pid):
        pids = set(get_pids(port))
        command = 'kill -9 {}'.format(' '.join([str(pid) for pid in pids]))
        os.system(command)
    else:
        print(f"No existing uvicorn process found on port {port}")
    
    module_name = "create_app"
    module = load_module(module_name,os.path.join(dir_path,"create_app.py"))
    if hasattr(module, "create_app"):
        module.create_app()
    # Since we don't use subprocess, os.popen gives us a way to capture stdout and stderr.
    subprocess.run([
        "uvicorn", "_gingerjs.main:app", "--reload",
        "--port", str(port),
        "--host", settings.get("HOST")
    ])

def run_command(cmd, env=None, cwd=None):
    logger.debug(f"Running command: {cmd}")
    process = subprocess.Popen(cmd, shell=True, env=env, cwd=cwd)
    process.wait()

def task_wrapper(func, name, *args, **kwargs):
    logger.debug(f"Starting task: {name}")
    return func(*args, **kwargs)

class ChangeHandler(FileSystemEventHandler):
    def __init__(self,my_env):
        self.settings = load_settings()
        self.my_env = my_env
        for key, value in self.settings.items():
            self.my_env[key] = str(value)
        # list of all processes, so that they can be killed afterwards 
        self.all_processes = []
        self.start()
    
    def debug_log(self, *args, **kwargs):
        if self.my_env["DEBUG"]:
            print(*args, **kwargs)

    def on_any_event(self, event):
        # Ignore events in __pycache__ directories
        if any(substring in event.src_path for substring in ["__pycache__","gingerJs_api_client","_gingerjs"])  or event.src_path.endswith(".py"):
            return
        if event.is_directory:
            return
        self.debug_log(f"* Detected change in {event.src_path} ,reloading")
        self.start()
        # self.start(event.src_path)

    def start(self):
        """Start the command in a new thread."""
        self.debug_log("Terminating Uvicorn process...")
        for process in self.all_processes:
            process.terminate()

        print("Starting new command thread...")
        process = multiprocessing.Process(target=run_uvicorn)
        process.start()
        self.all_processes.append(process)

class Execution_time ():
    def __init__ (self,start_time,name):
        self.start_time = start_time
        self.name = name

    def end(self,end_time):
        execution_time = end_time - self.start_time
        logger.debug(f"{self.name} Done","Execution Time:", execution_time, "seconds")


# base = os.path.join(os.getcwd(),"example","app")
base = os.path.join(os.getcwd())

def create_dir(directory):
    # Ensure the directory exists
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except Exception as e:
        # show error
        logger.error(e)

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
        logger.error(e)

def ignore_patterns(names,exclude={}):
    # Define the patterns you want to ignore
    return {name for name in names if name in exclude}

def copy_with_exceptions(src, dst, exclude=None,file_extension_mapping={}):
    if not os.path.exists(os.path.dirname(dst)):
        os.makedirs(os.path.dirname(dst))
    
    # Get the list of items in the source directory
    if not os.path.isdir(src):
        # Change the extension if the file extension is in the mapping
        src_ext = os.path.splitext(src)[1]
        if src_ext in file_extension_mapping:
            dst = os.path.splitext(dst)[0] + file_extension_mapping[src_ext]
        shutil.copy(src, dst)
        return
    
    items = os.listdir(src)
    
    # Precompute the set of items to ignore
    ignore_items = {name for name in items if name in exclude} if exclude else set()
    
    for item in items:
        if item in ignore_items:
            continue
        
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        
        if os.path.isdir(s):
            copy_with_exceptions(s, d,exclude,file_extension_mapping)
        else:
            item_ext = os.path.splitext(item)[1]
            if item_ext in file_extension_mapping:
                d = os.path.splitext(d)[0] + file_extension_mapping[item_ext]
            if not os.path.exists(os.path.dirname(d)):
                os.makedirs(os.path.dirname(d))
            shutil.copy(s, d)

def copy_file_if_not_exists(src, dst,exclude=None,file_extension_mapping={}):
    if os.path.exists(dst):
        click.echo(f"The file {src} already exists. Operation skipped.")
    else:
        if os.path.exists(src):
            copy_with_exceptions(src, dst,exclude,file_extension_mapping)
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
        '--extensions', '.js,.jsx,.tsx,.ts',
        './src',
        '-d', './_gingerjs/build'
    ]
    # Execute the command
    result = subprocess.run(command, capture_output=True, text=True,cwd=base)
    # Print the output
    if len(result.stderr):
        logger.error("stderr:", result.stderr)
    else:
        logger.info("stdout:", result.stdout)

@cli.command()
def build():
    """Builds the app using webpack config"""
    start_time = time.time()
    timing = Execution_time(start_time,"Building app")
    click.echo("Building app")
    settings = load_settings()
    my_env = os.environ.copy()
    my_env["DEBUG"] = str(settings.get("DEBUG",False))
    my_env["TYPESCRIPT"] = str(settings.get("TYPESCRIPT",False))
    my_env["STATIC_SITE"] = str(settings.get("STATIC_SITE",False))
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
        '--ext', 'jsx,tsx,js,ts,tsx,json',
        '--watch', './src',
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
        

def create_settings_file(config,base):
    config_content = f"""import os

NAME="{config["project_settings"]['project_name']}"
VERSION="{config["project_settings"]['version']}"
PACKAGE_MANAGER="{config["project_settings"]['package_manager']}"
DEBUG={config["project_settings"]['debug']}
PORT="{config["project_settings"]['port']}"
HOST="{config["project_settings"]['host']}"
PYTHONDONTWRITEBYTECODE="{config["project_settings"]['PYTHONDONTWRITEBYTECODE']}"
CWD={config["project_settings"]['CWD']}
STATIC_SITE={config["project_settings"]['static_site']}
TYPESCRIPT={config["project_settings"]["use_typescript"]}
TAILWIND={True if "Tailwind CSS" in config["create_app_settings"]['additional_configs']else False}
"""

    with open(os.path.join(base,"settings.py"), "w") as file:
        file.write(config_content)
    logger.info("\nConfiguration file 'config.py' created successfully.")

def create_package_json(config, package_json_path):
    with open(package_json_path, "r") as file:
        package_json = json.load(file)

    # Update project name and version
    package_json["name"] = config["project_settings"]["project_name"]
    package_json["version"] = config["project_settings"]["version"]

    # Define dependencies based on user input
    dependencies = package_json.get("dependencies", {})
    dev_dependencies = package_json.get("devDependencies", {})
    babel = package_json.get("babel",{})
    babel["presets"] = ["@babel/preset-env","@babel/preset-react"]
    babel["plugins"] = [
        ["module-resolver",{"root":["./"],"alias":{"@":"./src","src":"./src"}}],
        "@babel/plugin-transform-modules-commonjs"
    ]

    # Add or remove ShadCN dependency
    if config["create_app_settings"]["use_typescript"]:
        dev_dependencies["ts-loader"] = "^9.5.1"
        dev_dependencies["@babel/preset-typescript"] = "^7.24.7"
        babel["presets"].insert(1,"@babel/typescript")
    else:
        dev_dependencies.pop("ts-loader", None)
        dev_dependencies.pop("@babel/preset-typescript", None)

    # Add or remove ShadCN dependency
    if config["create_app_settings"]["use_shadcn"]:
        dependencies["@radix-ui/react-accordion"] = "^1.1.2"
        dependencies["@radix-ui/react-icons"] = "^1.3.0"
        
    else:
        dependencies.pop("@radix-ui/react-accordion", None)
        dependencies.pop("@radix-ui/react-icons", None)

    # Add or remove Tailwind CSS and related dependencies
    if "Tailwind CSS" in config["create_app_settings"]["additional_configs"]:
        dev_dependencies["tailwindcss"] = "^3.4.3"
        dev_dependencies["tailwind-merge"] = "^2.3.0"
        dev_dependencies["tailwindcss-animate"] = "^1.0.7"
        dev_dependencies["autoprefixer"] = "^10.4.19"
        dev_dependencies["postcss"] = "^8.4.38"
        dev_dependencies["postcss-loader"] = "^8.1.1"
        dev_dependencies["style-loader"] = "^4.0.0"
        dependencies["class-variance-authority"] = "^0.7.0"
        dependencies["clsx"] = "^2.1.1"
    else:
        dev_dependencies.pop("tailwindcss-animate", None)
        dev_dependencies.pop("tailwind-merge", None)
        dev_dependencies.pop("tailwindcss", None)
        dev_dependencies.pop("autoprefixer", None)
        dev_dependencies.pop("postcss", None)
        dev_dependencies.pop("postcss-loader", None)
        dev_dependencies.pop("style-loader", None)
        dependencies.pop("clsx", None)
        dependencies.pop("class-variance-authority", None)

    # Add or remove Jest dependencies
    if "Jest" in config["create_app_settings"]["additional_configs"]:
        dev_dependencies["jest"] = "^29.5.0"
        dev_dependencies["@types/jest"] = "^29.5.0"
    else:
        dev_dependencies.pop("jest", None)
        dev_dependencies.pop("@types/jest", None)

    # Update package.json
    package_json["dependencies"] = dependencies
    package_json["devDependencies"] = dev_dependencies

    if not config["project_settings"]["static_site"]:
        package_json["babel"] = babel

    with open(os.path.join(base,"package.json"), "w") as file:
        json.dump(package_json, file, indent=2)
    logger.info("\nCreated package.json")

def create_ts_js_config(config,config_json_path):
    with open(config_json_path, "r") as file:
        config_json = json.load(file)
    tsconfig = False
    include = config_json.get("include",["**/*.jsx", "**/*.js"])
    if config["create_app_settings"]["use_typescript"]:
        tsconfig = True
        include = ["**/*.tsx", "**/*.ts"]
    config_json["include"] = include

    with open(os.path.join(base,f'{"tsconfig" if tsconfig else "jsconfig"}.json'), "w") as file:
        json.dump(config_json, file, indent=2)
    logger.info("\nCreated",f'{"tsconfig" if tsconfig else "jsconfig"}.json')

@cli.command()
def create_app():
  """Intial project setup"""
  try:
    if not os.path.exists(os.path.join(base,"package.json")):
        config = main()
        create_settings_file(config,base)
        create_app_settigns = config["create_app_settings"]
        settings = load_settings()
        cwd = os.path.join(base)
        click.echo("Setting up app")
        create_package_json(config,os.path.join(dir_path,"app","package.json"))
        if "Tailwind CSS" in create_app_settigns['additional_configs']:
            copy_file_if_not_exists(os.path.join(dir_path,"app","tailwind.config.js"),os.path.join(cwd,"tailwind.config.js"))
            copy_file_if_not_exists(os.path.join(dir_path,"app","postcss.config.js"),os.path.join(cwd,"postcss.config.js"))
        if create_app_settigns['use_shadcn']:
            copy_file_if_not_exists(os.path.join(dir_path,"app","components.json"),os.path.join(cwd,"components.json"))
        create_ts_js_config(config,os.path.join(dir_path,"app","jsconfig.json"))
        copy_file_if_not_exists(os.path.join(dir_path,"app","public"),os.path.join(cwd,"public"),{"not_found.html","bad_request_exception_template.html","content.html","exception_template_debug.html","internal_server_exception_template.html","layout.html","exception_template.html",} if settings.get('STATIC_SITE') else {} )
        copy_file_if_not_exists(os.path.join(dir_path,"app","src"),os.path.join(cwd,"src"),{"api","index.py"} if settings.get('STATIC_SITE') else {},{".jsx":".tsx",".js":".ts"} if config['create_app_settings']['use_typescript'] else {})
        create_dir(os.path.join(cwd,"public","static"))
        copy_file_if_not_exists(os.path.join(dir_path,"app","public","static","gingerjs_logo.png"),os.path.join(cwd,"public","static","gingerjs_logo.png"))
        create_dir(os.path.join(cwd,"src","components"))
        click.echo("App set up completed")
    else:
        logger.info("Found a exsiting ginger app. Skipping intial setup")
        settings = load_settings()
        cwd = os.path.join(base)
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

        my_env = os.environ.copy()  # Copy the current environment
        settings = load_settings()
        if settings.get("STATIC_SITE",False):
            logger.info("This is a dev server, Change DEBUG to False to build production app")
            subprocess.run(["gingerjs","build"],check=True,env=my_env)
            return
        # Define the socket path
        socket_path = "/tmp/gingerjs_unix.sock"
        # Start the Node.js server as a subprocess
        node_process_path = os.path.join(dir_path, "..", "js_bridge", "unix_sock.js")
        LOCKFILE = "/tmp/my_subprocess.lock"
        if os.path.exists(LOCKFILE):
            click.echo("Another worker already started the subprocess.")
        else:
            node_process = subprocess.Popen(['node', node_process_path,f"debug={os.environ.get('DEBUG','False')}",f'cwd={os.getcwd()}',f"sock_path={socket_path}"])
            with open(LOCKFILE, "w") as f:
                f.write(str(node_process.pid))

        if mode == "dev":
            settings["DEBUG"] = True
            click.echo("Building app in in watch mode")
            event_handler = ChangeHandler(my_env)
            observer = Observer()
            observer.schedule(event_handler, path=f".{os.path.sep}src", recursive=True)  # Monitor current directory

            try:
                # Start the initial subprocess and begin watching for changes
                observer.start()
                click.echo("Watching for changes...")
                while True:
                    time.sleep(1)  # Keep the program running to watch for events
            except KeyboardInterrupt:
                click.echo("Exiting...")
                observer.stop()
            finally:
                observer.join()
            return
        
        settings["DEBUG"] = False

        try:
            module_name = "create_app"
            module = load_module(module_name,os.path.join(dir_path,"create_app.py"))
            if hasattr(module, "create_app"):
                module.create_app()
            
            subprocess.run([f"uvicorn","_gingerjs.main:app","--port",settings.get("PORT"),"--host",settings.get("HOST"),"--workers",settings.get("UVICORN_WORKERS","1")], check=True, cwd=base,env=my_env)
        except  Exception as e:
            raise e

    except Exception as e:
        click.echo(f"Error: {e}", err=True)

if __name__ == '__main__':
    cli()