
import click
import os
import subprocess
import shutil

ISDEV = False

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

@click.group()
def cli():
    pass

@cli.command()
def create_app():
  try:
    create_dir(base)
    click.echo("Setting up flask app")
    shutil.copy(f"{os.path.dirname(os.path.abspath(__file__))}/app/flask/main.py",base) # flask app
    click.echo("flask app set complete")
    click.echo("Setting up app")
    shutil.copy(f"{os.path.dirname(os.path.abspath(__file__))}/app/package.json",base)
    shutil.copy(f"{os.path.dirname(os.path.abspath(__file__))}/app/postcss.config.mjs",base)
    shutil.copy(f"{os.path.dirname(os.path.abspath(__file__))}/app/webpack.config.js",base)
    shutil.copy(f"{os.path.dirname(os.path.abspath(__file__))}/app/tailwind.config.js",base)
    shutil.copy(f"{os.path.dirname(os.path.abspath(__file__))}/app/.babelrc",base)
    shutil.copytree(src=f"{os.path.dirname(os.path.abspath(__file__))}/app/public/",dst=f"{base}/public/")
    shutil.copytree(src=f"{os.path.dirname(os.path.abspath(__file__))}/app/src/",dst=f"{base}/src/")
    click.echo("App set up completed")
    click.echo("Installing packages")
    if(ISDEV):
      click.echo("Setting up app for dev")
      subprocess.run(["yalc","add","react_py"], cwd=base)
    else:
      subprocess.run(["yarn","add","react_py"], cwd=base)
    subprocess.run(["yarn"], cwd=base)
    click.echo("Packages installed")
    click.echo("Run app by : gingerjs runserver")
  except subprocess.CalledProcessError as e:
        click.echo(f"Error: {e}", err=True)
        

@cli.command()
def runserver():
    """Run the main.py."""
    try:
        subprocess.run(["yarn", "webpack"], check=True, cwd=base)
        subprocess.run(["python","main.py"], check=True, cwd=base)
    except subprocess.CalledProcessError as e:
        click.echo(f"Error: {e}", err=True)

if __name__ == '__main__':
    cli()