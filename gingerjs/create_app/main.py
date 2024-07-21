
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

def find_process_by_port(port):
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            for conn in proc.connections():
                if conn.laddr.port == port:
                    return proc
        except psutil.AccessDenied:
            continue
        except psutil.NoSuchProcess:
            continue
    return None

def kill_process(process):
    try:
        process.terminate()  # or process.kill() for forceful termination
    except psutil.NoSuchProcess:
        pass

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, command,cwd):
        self.command = command
        self.process = None
        self.cwd = cwd
        self.settings = load_settings()
        self.my_env = os.environ.copy()  # Copy the current environment
        for key, value in self.settings.items():
            self.my_env[key] = str(value)
        self.my_env["DEBUG"] = str(True)
        for command in self.command:
            self.process = subprocess.run(command, shell=True,env=self.my_env)
    
    def debug_log(self, *args, **kwargs):
        if self.my_env["DEBUG"]:
            print(*args, **kwargs)

    def on_any_event(self, event):
        # Ignore events in __pycache__ directories
        if '__pycache__' in event.src_path:
            return
        if event.is_directory:
            return
        self.debug_log(f"* Detected change in {event.src_path} ,reloading")
        self.restart()

    def kill(self):
        if len(self.process):
            
            try:
                process_to_kill = find_process_by_port(self.settings.get("PORT"))
                if process_to_kill:
                    self.debug_log(f"Found process {process_to_kill.pid} on port {5001}. Killing...")
                    kill_process(process_to_kill)
                    self.debug_log("Process terminated.")
                else:
                    self.debug_log(f"No process found on port {self.settings.get('PORT')}.")
            except Exception as e:
                self.process.kill()

    def restart(self):
        self.kill()
        self.settings = load_settings()
        self.my_env = os.environ.copy()  # Copy the current environment
        for key, value in self.settings.items():
            self.my_env[key] = str(value)
        self.my_env["DEBUG"] = str(True)
        self.process = subprocess.Popen(self.command, shell=True,env=self.my_env)


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


processes = []

dir_path = os.path.dirname(os.path.abspath(__file__))
logger = Logger("create gingerjs")

debug = os.environ.get("debug", "False") == "True" or False

class Execution_time ():
    def __init__ (self,start_time,name):
        self.start_time = start_time
        self.name = name

    def end(self,end_time):
        execution_time = end_time - self.start_time
        print(f"{self.name} Done","Execution Time:", execution_time, "seconds")


def signal_handler(sig, frame):
    print("Ctrl+C captured, killing all processes...")
    for p in processes:
        try:
            p.terminate()
            print(f"Building on file change stopped")
        except Exception as e:
            print(f"Error terminating process {p.pid}: {e}")
            sys.exit(1)
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

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
        '-d', './build'
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
    my_env = os.environ.copy()
    create_app_process = subprocess.Popen(['python', f"{os.path.join(dir_path,'create_app.py')}"],env=my_env)
    processes.append(create_app_process)
        


@cli.command()
def create_app():
  """Intial project setup"""
  try:
    settings = load_settings()
    cwd = os.path.join(base)
    create_dir(cwd)
    copy_file_if_not_exists(f"{os.path.dirname(os.path.abspath(__file__))}/app/settings.py",os.path.join(cwd,"settings.py"),shutil.copy) # flask app
    click.echo("Setting up flask app")
    copy_file_if_not_exists(f"{os.path.dirname(os.path.abspath(__file__))}/app/main.py",os.path.join(cwd,"main.py"),shutil.copy) # flask app
    click.echo("flask app set complete")
    click.echo("Setting up app")
    copy_file_if_not_exists(f"{os.path.dirname(os.path.abspath(__file__))}/app/package.json",os.path.join(cwd,"package.json"),shutil.copy)
    copy_file_if_not_exists(f"{os.path.dirname(os.path.abspath(__file__))}/app/postcss.config.js",os.path.join(cwd,"postcss.config.js"),shutil.copy)
    copy_file_if_not_exists(f"{os.path.dirname(os.path.abspath(__file__))}/app/webpack.config.js",os.path.join(cwd,"webpack.config.js"),shutil.copy)
    copy_file_if_not_exists(f"{os.path.dirname(os.path.abspath(__file__))}/app/tailwind.config.js",os.path.join(cwd,"tailwind.config.js"),shutil.copy)
    copy_file_if_not_exists(f"{os.path.dirname(os.path.abspath(__file__))}/app/jsconfig.json",os.path.join(cwd,"jsconfig.json"),shutil.copy)
    copy_file_if_not_exists(f"{os.path.dirname(os.path.abspath(__file__))}/app/components.json",os.path.join(cwd,"components.json"),shutil.copy)
    copy_file_if_not_exists(f"{os.path.dirname(os.path.abspath(__file__))}/app/public/",f"{cwd}/public/", shutil.copytree)
    copy_file_if_not_exists(f"{os.path.dirname(os.path.abspath(__file__))}/app/src/",f"{cwd}/src/", shutil.copytree)
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
            click.echo("Building app in in watch mode")
            path = "./src"
            command = " ".join(["gingerjs","build","&&","uvicorn","main:app","--port",settings.get("PORT"),"--host",settings.get("HOST")])
            event_handler = ChangeHandler(command,base)
            observer = Observer()
            observer.schedule(event_handler, path, recursive=True)
            observer.start()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.kill()
                observer.stop()
            observer.join()
            return
        
        my_env["GINGERJS_APP_DIR"] = base
        for key, value in settings.items():
            my_env[key] = str(value)

        build_node_process = None
        node_process = None
        try:
            build_node_process = subprocess.run(["gingerjs","build"], check=True,cwd=base,env=my_env)
            node_process = subprocess.run(["uvicorn","main:app","--port",settings.get("PORT"),"--host",settings.get("HOST")], check=True, cwd=base,env=my_env)
        except  Exception as e:
            if build_node_process is not None:
                build_node_process.kill()
            if node_process is not None:
                node_process.kill()

    except subprocess.CalledProcessError as e:
        click.echo(f"Error: {e}", err=True)

if __name__ == '__main__':
    cli()