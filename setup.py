from setuptools import setup, find_packages

packages = find_packages()

setup(
    name='ginger_js',  # Replace with your package name
    version='0.0.2',  # Replace with your package version
    author='py-react',  # Replace with your name
    author_email='yksandeep08+reactpy@gmail.com',  # Replace with your email
    description='A Truly Full-Stack Development Experience with Python and React',  # Replace with a short description
    long_description=open('readme.md').read(),  # Ensure you have a README.md file
    long_description_content_type='text/markdown',  # Use 'text/x-rst' if your README is in reStructuredText
    url='https://github.com/ginger-society/ginger-js',  # Replace with the URL of your package's repository
    packages=packages,  # Automatically find and include your packages
    classifiers=[
        'License :: OSI Approved :: MIT License',  # Replace with your license
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11.0',  # Specify the minimum Python version required
    install_requires=[
        # List your package dependencies here, e.g.:
        "fastapi==0.111.1",
        "watchdog==4.0.1",
        "psutil==6.0.0"
    ],
    entry_points={
        'console_scripts': [
            'gingerjs=gingerjs.create_app.main:cli',  # Replace with your console script entry points
        ],
    },
    include_package_data=True,  # Include additional files specified in MANIFEST.in
)
