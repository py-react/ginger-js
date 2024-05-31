
import click
import os
import subprocess
import shutil

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
def create_app():
  try:
    create_dir(base)
    click.echo("Setting up flask app")
    copy_file_if_not_exists(f"{os.path.dirname(os.path.abspath(__file__))}/app/flask/main.py",os.path.join(base,"main.py"),shutil.copy) # flask app
    click.echo("flask app set complete")
    click.echo("Setting up app")
    copy_file_if_not_exists(f"{os.path.dirname(os.path.abspath(__file__))}/app/package.json",os.path.join(base,"package.json"),shutil.copy)
    copy_file_if_not_exists(f"{os.path.dirname(os.path.abspath(__file__))}/app/postcss.config.js",os.path.join(base,"postcss.config.js"),shutil.copy)
    copy_file_if_not_exists(f"{os.path.dirname(os.path.abspath(__file__))}/app/webpack.config.js",os.path.join(base,"webpack.config.js"),shutil.copy)
    copy_file_if_not_exists(f"{os.path.dirname(os.path.abspath(__file__))}/app/tailwind.config.js",os.path.join(base,"tailwind.config.js"),shutil.copy)
    copy_file_if_not_exists(f"{os.path.dirname(os.path.abspath(__file__))}/app/jsconfig.json",os.path.join(base,"jsconfig.json"),shutil.copy)
    copy_file_if_not_exists(f"{os.path.dirname(os.path.abspath(__file__))}/app/components.json",os.path.join(base,"components.json"),shutil.copy)
    copy_file_if_not_exists(f"{os.path.dirname(os.path.abspath(__file__))}/app/public/",f"{base}/public/", shutil.copytree)
    copy_file_if_not_exists(f"{os.path.dirname(os.path.abspath(__file__))}/app/src/",f"{base}/src/", shutil.copytree)
    create_dir(f"{os.path.dirname(os.path.abspath(__file__))}/app/src/components")
    create_dir(f"{os.path.dirname(os.path.abspath(__file__))}/app/src/libs")
    click.echo("App set up completed")
    click.echo("Installing packages")
    subprocess.run(["yarn"], cwd=base)
    click.echo("Packages installed")
    click.echo("Before running the app run:")
    click.echo("yarn add ginger_js")
    click.echo("Run your app using gingerjs cli : gingerjs runserver")
  except subprocess.CalledProcessError as e:
        click.echo(f"Error: {e}", err=True)
        

@cli.command()
def runserver():
    """Run the main.py."""
    try:
        subprocess.run(["yarn", "gingerJs" ,"build"], check=True, cwd=base)
        subprocess.run(["python","main.py"], check=True, cwd=base)
    except subprocess.CalledProcessError as e:
        click.echo(f"Error: {e}", err=True)

if __name__ == '__main__':
    cli()