
import click
import os
import subprocess
import shutil
import os
import signal
import sys
import time
from gingerjs.create_app.load_settings import load_settings


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
        copyFunc(src, dst)
        click.echo(f"Copied {src} to {dst}.")

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
    subprocess.run(['python', f"{os.path.join(dir_path,'create_app.py')}"], check=True,env=my_env)
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

    subprocess.run(command,cwd=base,env=my_env)

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
    copy_file_if_not_exists(f"{os.path.dirname(os.path.abspath(__file__))}/app/flask/main.py",os.path.join(cwd,"main.py"),shutil.copy) # flask app
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
    create_dir(f"{os.path.dirname(os.path.abspath(__file__))}/app/src/components")
    create_dir(f"{os.path.dirname(os.path.abspath(__file__))}/app/src/libs")
    click.echo("App set up completed")
    click.echo("Installing packages")
    package_manager = settings.get('PACKAGE_MANAGER')
    subprocess.run(["yarn" if package_manager == "yarn" else "npm", "install"], cwd=cwd)
    click.echo("Packages installed")
    click.echo("Run your app using : gingerjs runserver")
  except subprocess.CalledProcessError as e:
        click.echo(f"Error: {e}", err=True)

@cli.command()
def runserver():
    """Runs the webapp"""
    try:
        settings = load_settings()
        my_env = os.environ.copy()  # Copy the current environment
        my_env["GINGERJS_APP_DIR"] = base
        for key, value in settings.items():
            my_env[key] = str(value)
        subprocess.run(["gingerjs","build"], check=True,cwd=base,env=my_env)
        subprocess.run(["python","main.py"], check=True, cwd=base,env=my_env)
    except subprocess.CalledProcessError as e:
        click.echo(f"Error: {e}", err=True)





if __name__ == '__main__':
    cli()