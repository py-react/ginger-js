import subprocess
import inquirer

def check_node_installed():
    try:
        result = subprocess.run(["node", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode().strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def check_yarn_installed():
    try:
        result = subprocess.run(["yarn", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode().strip()
    except Exception as e:
        print(e)
        return None

def install_node():
    print("\nNode.js is not installed. Installing Node.js...")
    # This is for demonstration purposes. Adjust as needed for your environment.
    subprocess.run(["curl", "-fsSL", "https://fnm.vercel.app/install"], check=True)
    print("Node.js installed successfully.\n")

def install_yarn():
    print("\nInstalling Yarn...")
    subprocess.run(["npm", "install", "-g", "yarn"], check=True)
    print("Yarn installed successfully.\n")

def main():
    
    # Step 1: Ask for project name
    project_name = inquirer.text(
        message="What is your project named?",
        default="my-app"
    )

    # Check if Node.js is installed
    node_version = check_node_installed()
    if node_version:
        print(f"Node.js is already installed (version: {node_version}). Skipping installation.")
    else:
        install_node_confirmation = inquirer.confirm(
            message="Node.js is not installed. Would you like to install it?",
            default=True
        )
        if install_node_confirmation:
            install_node()
        else:
            print("Node.js is required to create the project. Exiting.")
            return

    # Ask which package manager to use
    package_manager_choices = ["npm", "yarn"]
    package_manager = inquirer.list_input(
        message="Which package manager would you like to use?",
        choices=package_manager_choices,
        default="npm"
    )

    if package_manager == "yarn":
        yarn_version = check_yarn_installed()
        print(yarn_version)
        if yarn_version:
            print(f"Yarn is already installed (version: {yarn_version}). Skipping installation.")
        else:
            print(f"Yarn not found installing...")
            install_yarn()


    # Step 2: Optional configuration for TypeScript
    use_typescript = inquirer.confirm(
        message="Would you like to use TypeScript?",
        default=False
    )

    # Step 3: Additional configurations
    additional_configs = inquirer.checkbox(
        message="Select additional configurations:",
        choices=[
            "Jest",
            "Tailwind CSS",
            "None"
        ],
        default=[]
    )

    # Step 4: Conditional prompt for ShadCN based on Tailwind CSS selection
    if "Tailwind CSS" in additional_configs:
        use_shadcn = inquirer.confirm(
            message="Would you like to use ShadCN with Tailwind CSS?",
            default=False
        )
    else:
        use_shadcn = inquirer.confirm(
            message="Would you like to use ShadCN? This will add Tailwind CSS by default.",
            default=False
        )
        if use_shadcn:
            additional_configs.append("Tailwind CSS")

    # Step 5: Ask if the site should be static
    use_static_site = inquirer.confirm(
        message="Do you want to create a static site?",
        default=True
    )

    config = {}
    config["project_settings"] = {
        "project_name": project_name,
        "version": "1.0",
        "package_manager": package_manager,
        "debug": False,
        "port": "5001",
        "host": "0.0.0.0",
        "PYTHONDONTWRITEBYTECODE": "",
        "CWD": "__file__",
        "static_site": use_static_site,
        "use_typescript":use_typescript
    }
    config["create_app_settings"] = {
        "use_typescript":use_typescript,
        "use_shadcn":use_shadcn,
        "additional_configs":additional_configs
    }

    # Create configuration file
    return config

