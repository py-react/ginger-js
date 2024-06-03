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
        "asgiref==3.8.1",
        "blinker==1.8.1",
        "certifi==2024.2.2",
        "charset-normalizer==3.3.2",
        "click==8.1.7",
        "Flask==3.0.3",
        "Flask-Cors==4.0.1",
        "idna==3.7",
        "itsdangerous==2.2.0",
        "Jinja2==3.1.3",
        "MarkupSafe==2.1.5",
        "requests==2.31.0",
        "six==1.16.0",
        "sqlparse==0.5.0",
        "tornado==6.4",
        "urllib3==2.2.1",
        "Werkzeug==3.0.2"
    ],
    entry_points={
        'console_scripts': [
            'gingerjs=gingerjs.create_app.main:cli',  # Replace with your console script entry points
        ],
    },
    include_package_data=True,  # Include additional files specified in MANIFEST.in
)
