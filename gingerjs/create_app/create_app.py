import os
import re
import subprocess
from gingerjs.create_app.load_settings import load_settings
import shutil
import importlib.util


# Function to copy files and directories only if they don't exist at the destination
def copy_if_not_exists(src, dest):
    if not os.path.exists(dest):
        if os.path.isdir(src):
            shutil.copytree(src, dest)
        else:
            shutil.copy2(src, dest)

def load_module(module_name,module_path):
    try:
        module_name = module_name
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        raise e

def copy_file_if_not_exists(src, dst,copyFunc):
    if os.path.exists(dst):
        logger.debug(f"The file {src} already exists. Operation skipped.")
    else:
        if os.path.exists(src):
            copyFunc(src, dst)
            logger.debug(f"Copied {src} to {dst}.")
        else:
            logger.debug(f"The file {src} doesn't exists. Operation skipped.")
            raise f"The file {src} doesn't exists"

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

logger = Logger("create-react-app")
DEFAULT_LAYOUT = "DefaultLayout_"
PAGE_NOT_FOUND = "GenericNotFound"
DEFAULT_LOADER = "DefaultLoader_"
dir_path = os.path.dirname(os.path.abspath(__file__))
base = os.path.join(os.getcwd())

# Function to recursively search for JSX files and create a list of absolute paths
def find_jsx_files(directory_path, jsx_files_list=None):
    if jsx_files_list is None:
        jsx_files_list = []
    
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".jsx"):
                jsx_files_list.append(os.path.join(root, file))
    
    return jsx_files_list

def replace_wildcards_in_component_name(path):
    # Define the regex pattern to match any text within square brackets
    pattern = re.compile(r"\[([^\]]+)\]")
    # Replace the matching segments with : followed by the captured text
    return pattern.sub(r"_\1_", path)

def generate_component_name(component_path):
    return replace_wildcards_in_component_name(
        "_".join(
            part.capitalize() for part in component_path.split("/")[3:]
        ).replace("-", "_").replace(".jsx", "")
    )

def replace_wildcards(path):
    if path == "/":
        return "*"
    # Define the regex pattern to match any text within square brackets
    pattern = re.compile(r"\[([^\]]+)\]")
    # Replace the matching segments with : followed by the captured text
    return pattern.sub(r":\1", path)

def create_routes(data, parent_path="/",last_path="",parentLoader="", debug=False):
    routes = []
    parent = parent_path
    loader = DEFAULT_LOADER if  parentLoader=="" else parentLoader
    full_parent_path = last_path + "/" + replace_wildcards(parent).replace('*','') if replace_wildcards(parent) != "*" else last_path  + replace_wildcards(parent).replace('*','')
    layout_comp = DEFAULT_LAYOUT
    page_not_found = PAGE_NOT_FOUND

    # TODO :get 404 page and other
    if "layout.jsx" in data:
        layout_comp = generate_component_name(data["layout.jsx"])
    elif "layout.jsx" not in data and parent_path == "/":
        layout_comp = DEFAULT_LAYOUT

    if "page_not_found.jsx" in data:
        page_not_found = generate_component_name(data["page_not_found.jsx"])

    if "loading.jsx" in data:
        loader = generate_component_name(data["loading.jsx"])

    if "index.jsx" in data:
        routes.append(f"""
                <Route path="{replace_wildcards(parent)}" 
                    element = {{
                        <LayoutPropsProvider forUrl={{"{full_parent_path+"/"}"}} Element={{{layout_comp}}} {{...props}}/>
                    }}
                    
                >
        """)
        for key in data:
            route_path = data["index.jsx"].split("app")[1].replace("/index.jsx", "")
            if key not in {"index.jsx", "layout.jsx", "app.jsx", "loading.jsx","page_not_found.jsx"}:
                routes.extend(create_routes(data[key], key, full_parent_path,loader, debug))
            elif key not in {"layout.jsx", "app.jsx", "loading.jsx","page_not_found.jsx"}:
                component_name = generate_component_name(data["index.jsx"])
                add_path = f'path="{replace_wildcards(route_path).replace(f"/{parent}", "")}"'
                sub_paths = route_path.split("/")
                routes.append(f'''
                    <Route {"index" if sub_paths[-1] == parent_path or route_path in ["", "/src/"] else add_path}
                        element={{
                            <>
                                <PropsProvider Element={{{component_name}}} Fallback={{{loader}}} {{...props}} />
                            </>
                        }}
                    />
                ''')
        routes.append('</Route>')
        if page_not_found is not None:
            routes.append(f'<Route path="*" element={{<{page_not_found} />}}/>')
        if page_not_found is None and parent == "/":
            routes.append(f'<Route path="*" element={{<{PAGE_NOT_FOUND} />}}/>') 
    return routes

def generic_not_found():
    return """
    import React from 'react';

    const GenericNotFound = () => {
        return (
            <div style={{
                height:"100vh",
            }} className="flex items-center justify-center bg-white dark:bg-gray-950 px-4 md:px-6">
                <div className="max-w-md text-center space-y-4">
                    <h1 style={{fontSize: "8rem", lineHeight: "1", color: "rgb(17 24 39)"}} 
                        className="font-bold text-gray-900 dark:text-gray-50"
                    >
                        404
                    </h1>
                    <p style={{fontSize: "1.125rem",color: "rgb(107 114 128)"}} className="dark:text-gray-400">
                        Oops, the page you are looking for could not be found.
                    </p>
                </div>
            </div>
        )
    }

    export default GenericNotFound;
    """


def generate_error_component():
    return '''
    import React from 'react';

    const ErrorMessage = ({hasError,error,...props }) => {
        const parseErrorMessage = (data) => {
            const msgStartIndex = data.indexOf('data-msg="') + 'data-msg="'.length;
            const msgEndIndex = data.indexOf('"', msgStartIndex);
            const msg = data.substring(msgStartIndex, msgEndIndex).replace(/&quot;/g, '"');

            const stackStartIndex = data.indexOf('data-stck="') + 'data-stck="'.length;
            const stackEndIndex = data.indexOf('"', stackStartIndex);
            const stack = data.substring(stackStartIndex, stackEndIndex).replace(/\\n/g, '\\n');
            console.error(msg, stack)
            return { msg, stack };
        };

        if (hasError) {
            const { msg, stack } = parseErrorMessage(error);
            return (
                <div className="fixed inset-0 flex items-center justify-center z-50">
                    <div className="bg-white rounded-md shadow-lg p-8 max-w-screen-2xl w-full">
                        <h2 className="text-lg font-semibold mb-2 text-red-600">Error</h2>
                        <p className="mb-4 text-gray-800">{msg}</p>
                        <pre className="bg-red-100 p-4 rounded overflow-x-auto text-red-700">{stack}</pre>
                    </div>
                </div>
            );
        } else {
            return <>{props.children}</>
        }
    };

    export default ErrorMessage;
    '''

def generate_lazy_component(debug=False):
    error_component = "Error {...props}" if debug else ""
    error_component_closing = "Error" if debug else ""
    return f'''
    const LazyComp = ({{ LazyComponent, Loader, ...props }}) => {{
        const [shouldRenderLazy, setShouldRenderLazy] = useState(false);
        useEffect(() => {{
            setShouldRenderLazy(true);
        }}, []);
        const LazyIndex = shouldRenderLazy ? LazyComponent : Loader

        return (
            <>
                {{shouldRenderLazy && (
                    <{error_component}> 
                        {{LazyIndex}}
                    </{error_component_closing}> 
                )}}
            </>
        );
    }};
    '''

def generate_debug_error_component():
    return '''
    class ErrorBoundary extends React.Component {
        constructor(props) {
            super(props);
            this.state = { hasError: false};
        }

        static getDerivedStateFromError(error) {
            return { hasError: true };
        }

        componentDidCatch(err, errorInfo) {
            console.log({ err, errorInfo },'findMe')
        }

        render() {
            if (this.state.hasError) {
                return (
                    <>
                        <div className="fixed inset-0 flex items-center justify-center z-50">
                            <div className="bg-white rounded-md shadow-lg p-8 max-w-screen-2xl w-full">
                                <h2 className="text-lg font-semibold mb-2 text-red-600">Client Error</h2>
                                <p className="mb-4 text-gray-800">{this.state.msg}</p>
                                <pre className="bg-red-100 p-4 rounded overflow-x-auto text-red-700">{this.state.stack}</pre>
                            </div>
                        </div>
                    </>
                );
            }
            return this.props.children; 
        }
    }
    '''

def generate_import_statements(obj):
    imports = []

    def traverse(node, path):
        nonlocal imports
        if isinstance(node, str):
            component_name = generate_component_name(node)
            if os.path.sep+"app.jsx" not in node:
                file_data = open(node, "r").read()
                # if "use client" in file_data:
                imports.append(f"""const {component_name} = React.lazy(() => import('{node.replace(os.path.sep.join(["","src",""]), os.path.sep.join(["","_gingerjs","build",""])).replace(".jsx", ".js")}'));""")
                # else:
                # imports.append(f'import {component_name} from "{node.replace("/src/", "/build/").replace(".jsx", ".js")}";')

        else:
            for key in node:
                traverse(node[key], f'{path}/{key}')

    traverse(obj, "")
    return "\n".join(imports)

def create_react_app_with_routes(paths, debug):
    def create_nodes(components_paths, nodes=None):
        if nodes is None:
            nodes = {}
        for component_path in components_paths:
            relative_path = component_path.split("src")[1]
            paths = list(filter(None, relative_path.split(os.path.sep)))  # Remove empty strings from split
            current = nodes
            for i in range(len(paths) - 1):
                key = paths[i]
                current = current.setdefault(key, {})
            current[paths[-1]] = component_path
        return nodes

    node_data = create_nodes(paths)

    importErrCompo = f'import Error from ".{os.path.sep}Error"' if debug else ""

    to_return = [
        f"""
        import React, {{ useState, useEffect,useRef,useCallback }} from 'react';
        {importErrCompo}
        import GenericNotFound from ".{os.path.sep}GenericNotFound"   
        import {{ BrowserRouter as Router, Route, Routes, Outlet, useLocation }} from 'react-router-dom';     
        import {{ Redirect, matchPath }} from 'react-router';

        {generate_import_statements(node_data)}
        

        const DefaultLayout_ = React.memo(()=>{{
            return <Outlet/>
        }})


        const DefaultLoader_ = ({{isLoading}}) => {{
            const [progress, setProgress] = useState(0);
            const [loading, setLoading] = useState(isLoading);
            useEffect(() => {{
                let interval;
                if (isLoading) {{
                setLoading(true);
                setProgress(0);
                interval = setInterval(() => {{
                    setProgress((prev) => {{
                        if (prev < 90) {{
                            if(prev+1===100){{
                                return prev
                            }}
                            return prev + 0.5; // Adjust the increment as needed for smoother progress
                        }}
                        return prev;
                    }});
                }}, 50); // Adjust the interval duration as needed
                }} else {{
                    setProgress(100); // complete the progress bar
                    setTimeout(() => setLoading(false), 500); // wait for the completion transition
                }}

                return () => clearInterval(interval);
            }}, [isLoading]);

            if (!loading) return null;
            return (
                <div className="backdrop">
                    <div className="progress-bar" style={{{{ width: `${{progress}}%` }}}}></div>
                    <noscript>
                        <div style={{{{color:"#fff"}}}}>Your browser does not support JavaScript!</div>
                    </noscript>
                </div>
            );
        }};


        const PropsProvider = ({{Element,Fallback,...props}})=>{{
            const location = useLocation()
            const [loading,setLoading] = useState(true)

            const [propsData,setPropData] = useState(()=>(()=>{{
                try {{
                    const data  = JSON.parse(JSON.stringify(window.flask_react_app_props))
                    return data
                }}catch(err){{
                    return props
                }}
            }})())

            useEffect(()=>{{
                setLoading(true)
                React.startTransition(() => {{
                    const data  = JSON.parse(JSON.stringify(window.flask_react_app_props))
                    setPropData(data)
                    setLoading(false)
                }});
                return ()=>{{
                    setLoading(false)
                }}
            }},[location])
            
            return (
                <React.Suspense fallback={{<Fallback isLoading={{true}} />}}>
                    <Element {{...propsData}} />
                    <Fallback isLoading={{loading}} />
                </React.Suspense >
            )
        }}

        const LayoutPropsProvider = ({{Element,Fallback , forUrl, ...props}})=>{{
            const location = useLocation();
            const [propsData,setPropsData] = useState((()=>{{
                if ("layout_props" in props) {{
                    const layouts = Object.keys(props.layout_props).filter((key) => {{
                        if (location.pathname.includes(key)) {{
                            return {{ ...props.layout_props[key], location: props.location }};
                        }}
                    }});
                    let currentLayoutProp = undefined
                    for(let i=0;i<layouts.length;i++){{
                        if(matchPath({{ path: layouts[i], exact: true }},forUrl)){{
                            currentLayoutProp = props.layout_props[layouts[i]]
                            break
                        }}
                    }}
                    if(currentLayoutProp){{
                        return currentLayoutProp
                    }}else{{
                        return props;
                    }}
                    // return props;
                }} else {{
                    return props;
                }}
            }})())

            useEffect(()=>{{
                const data  = JSON.parse(JSON.stringify(window.flask_react_app_props))
                if ("layout_props" in data){{
                    Object.keys(data.layout_props).map(key=>{{
                        if (location.pathname.includes(key) && matchPath({{ path: location.pathname, exact: true }},forUrl)){{
                            React.startTransition(()=>{{
                                setPropsData({{...data.layout_props[key],location:props.location}})
                            }})
                        }}
                    }})

                }}
                
            }},[location])

            const Elem = React.useMemo(()=>{{
                return <Element {{...propsData}} />
            }},[propsData])
            
            return (
                <React.Suspense fallback={{<></>}}>
                    <>
                        {{Elem}}
                    </>
                </React.Suspense>
            )
        }}

        {generate_lazy_component(debug)}

        {generate_debug_error_component()}
        """
    ]
    to_return.append("const App = (props) => {")
    to_return.append("return (")
    to_return.append(f"""
            <{"Error {...props}" if debug else ""} >
    """)
    to_return.append("""<Routes>""")
    to_return.append("\n".join(create_routes(data=node_data["app"], debug=debug)))
    to_return.append("""</Routes>""")
    to_return.append(f"""
            </{"Error" if debug else ""}>
    """)
    to_return.append(""");""")
    to_return.append(
        """
        }
        export default App
        """)

    return "\n".join(to_return)

def generate_main_client_entry():
    return f'''
    import React,{{useState,useEffect}} from 'react';
    import Router from ".{os.path.sep}BrowserRouterWrapper"
    import ReactDOM from 'react-dom';
    import {{ hydrateRoot,createRoot }} from 'react-dom{os.path.sep}client';
    import App from ".{os.path.sep}app"
    function getServerProps(props) {{
        try {{
            if (window !== undefined) {{
                const data  = JSON.parse(JSON.stringify(window.flask_react_app_props))
                return {{ ...data,...props }};
            }}
        }} catch (error) {{
            // pass
        }}
        return props;
    }}
    function handleHydrationError(error,errorInfo) {{
        console.error('Hydration error:', {{error,errorInfo}});

        // Create the error overlay elements
        const overlay = document.createElement('div');
        overlay.id = 'error-overlay';

        const messageBox = document.createElement('div');
        messageBox.id = 'error-message';

        const closeButton = document.createElement('button');
        closeButton.id = 'close-overlay';
        closeButton.textContent = 'Close';

        const title = document.createElement('h2');
        title.textContent = error.message;

        const details = document.createElement('pre');
        details.id = 'error-details';
        details.innerHTML = error.stack;

        // Append elements
        messageBox.appendChild(closeButton);
        messageBox.appendChild(title);
        messageBox.appendChild(details);
        overlay.appendChild(messageBox);
        document.body.appendChild(overlay);

        // Add styles using JavaScript
        overlay.style.position = 'fixed';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100%';
        overlay.style.height = '100%';
        overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
        overlay.style.color = 'white';
        overlay.style.display = 'flex';
        overlay.style.justifyContent = 'center';
        overlay.style.alignItems = 'center';
        overlay.style.zIndex = '1000';

        messageBox.style.background = "rgba(254, 226, 226,1)";
        messageBox.style.padding = '20px';
        messageBox.style.borderRadius = '5px';
        messageBox.style.maxWidth = '80%';
        messageBox.style.maxHeight = '80%';
        messageBox.style.overflow = 'auto';
        messageBox.style.color = 'rgb(185, 28, 28 ,1 )';

        title.style.marginTop = '0';

        details.style.whiteSpace = 'pre-wrap';
        details.style.marginTop = '10px';

        closeButton.style.backgroundColor = '#ff5e5e';
        closeButton.style.border = 'none';
        closeButton.style.borderRadius = '4px';
        closeButton.style.color = 'white';
        closeButton.style.padding = '8px';
        closeButton.style.cursor = 'pointer';
        closeButton.style.float = 'right';

        closeButton.addEventListener('mouseover', () => {{
        closeButton.style.backgroundColor = '#ff1e1e';
        }});

        closeButton.addEventListener('mouseout', () => {{
        closeButton.style.backgroundColor = '#ff5e5e';
        }});

        // Close button functionality
        closeButton.addEventListener('click', () => {{
        overlay.style.display = 'none';
        }});
        throw new Error(error)

        // Run your specific function here
        // e.g., log to a service, display a fallback UI, etc.
    }}
    
    const container = document.getElementById("root");

    const timeOfRender = new Date()
  
    window.__REACT_HYDRATE__ = function(url){{
        if(!container) return
        hydrateRoot(container,<React.StrictMode><Router><App {{...getServerProps({{}})}}/></Router></React.StrictMode>,{{onRecoverableError:handleHydrationError}});
    }}
    window.__REACT_HYDRATE__()

    // Function to handle navigation events
    function handleNavigation(event) {{
        if(event.state !== null){{
            window.flask_react_app_props = event.state
        }}
        // Run your custom function here based on the navigation state
    }}

    document.addEventListener('DOMContentLoaded', function() {{
        // Define your initial state object
        const initialState = window.flask_react_app_props;

        // Replace or push state as needed
        history.replaceState(initialState, document.title, window.location.href);

        // Optionally, dispatch a popstate event to notify the app of the initial state
        window.dispatchEvent(new PopStateEvent('popstate', {{ state: initialState }}));
        
        // Add event listener for 'popstate' events
        window.addEventListener('popstate', handleNavigation);
    }});

    '''

def generate_browser_router_wrapper():
    return '''
    import React from 'react';
    import { BrowserRouter } from 'react-router-dom';

    function Router({children}){
      return (
        <BrowserRouter>
          {children}
        </BrowserRouter>
      )
    }

    export default Router
    '''

def generate_static_router_wrapper():
    return '''
    import React from 'react';
    import { StaticRouter } from "react-router-dom/server";

    function Router({children,url}){
      return (
        <StaticRouter location={url}>
          {children}
        </StaticRouter>
      )
    }

    export default Router
    '''

def build_changes(path):
    settings = load_settings()
    package_manager = settings.get('PACKAGE_MANAGER')
    my_env = os.environ.copy()
    debug = settings.get("DEBUG") or False
    if not debug:
        assert "Debug mode is not activated"
    cwd = os.getcwd()
    destination = path.replace(os.path.sep.join(["","src",""]),os.sep.join(["","_gingerjs","build",""]))

    subprocess.run(["yarn" if package_manager == "yarn" else "npx", "babel", "--extensions", ".js,.jsx", path, "-d", os.path.dirname(destination)], cwd=base,check=True,env=my_env)
    print("Building app...")
    subprocess.run(["yarn" if package_manager == "yarn" else "npx", "webpack","--config",os.path.dirname(__file__)+os.sep+"webpack.config.js", "--stats-error-details"], cwd=base, check=True, env=my_env)
    # Construct the source and destination paths
    source_path = os.path.join(base, 'public', 'static')
    destination_path = os.path.join(base, '_gingerjs', 'build', 'static')
    # Iterate through the source directory
    for root, dirs, files in os.walk(source_path):
        for name in dirs:
            src_dir = os.path.join(root, name)
            dest_dir = os.path.join(destination_path, os.path.relpath(src_dir, source_path))
            copy_if_not_exists(src_dir, dest_dir)
        for name in files:
            src_file = os.path.join(root, name)
            dest_file = os.path.join(destination_path, os.path.relpath(src_file, source_path))
            copy_if_not_exists(src_file, dest_file)
    os.remove(os.path.join(cwd,"_gingerjs","__init__.py"))
    with open(os.path.join(cwd,"_gingerjs","__init__.py"), 'w') as file:
            pass  # 'pass' is used here to do nothing, effectively creating an empty file
    

def create_app():
    settings = load_settings()
    package_manager = settings.get('PACKAGE_MANAGER')
    my_env = os.environ.copy()
    debug = settings.get("DEBUG") or False
    cwd = os.getcwd()
    if cwd is None:
        raise ValueError("Current working directory not provided")

    try:
        # Remove the './build' directory
        build_path = os.path.join(cwd,"_gingerjs")
        if os.path.exists(build_path):
            shutil.rmtree(build_path)

        # Remove the './public/static/js/app.js' file
        app_js_path = os.path.join(cwd, 'public', 'static', 'js', 'app.js')
        if os.path.exists(app_js_path):
            os.remove(app_js_path)
        # subprocess.run(["rm", "-rf", "./build"], check=True,cwd=cwd)
        # subprocess.run(["rm", "-rf", "./__build__"], check=True,cwd=cwd)
        # subprocess.run(["rm", "./public/static/js/app.js"], check=True,cwd=cwd)
    except subprocess.CalledProcessError:
        pass

    os.makedirs(os.path.join(cwd,"_gingerjs"), exist_ok=True)
    copy_file_if_not_exists(os.path.join(dir_path,"app","main.py"),os.path.join(cwd,"_gingerjs","main.py"),shutil.copy) # flask app
    with open(os.path.join(cwd,"_gingerjs","__init__.py"), 'w') as file:
        pass  # 'pass' is used here to do nothing, effectively creating an empty file

    os.makedirs(os.path.join(cwd,"_gingerjs","__build__"), exist_ok=True)

    with open(os.path.join(cwd,"_gingerjs", "__build__", "app.jsx"), "w") as file:
        file.write(create_react_app_with_routes(find_jsx_files(os.path.join(cwd, "src", "app")), debug))

    with open(os.path.join(cwd,"_gingerjs", "__build__", "BrowserRouterWrapper.jsx"), "w") as file:
        file.write(generate_browser_router_wrapper())

    with open(os.path.join(cwd,"_gingerjs", "__build__", "StaticRouterWrapper.jsx"), "w") as file:
        file.write(generate_static_router_wrapper())

    with open(os.path.join(cwd,"_gingerjs", "__build__", "main.jsx"), "w") as file:
        file.write(generate_main_client_entry())

    if debug:
        with open(os.path.join(cwd,"_gingerjs", "__build__", "Error.jsx"), "w") as file:
            file.write(generate_error_component())

    with open(os.path.join(cwd,"_gingerjs", "__build__", "GenericNotFound.jsx"), "w") as file:
        file.write(generic_not_found())

    subprocess.run(["yarn" if package_manager == "yarn" else "npx", "babel", "--extensions", ".js,.jsx", os.path.sep.join([".","","_gingerjs","__build__"]), "-d", os.path.sep.join([".","","_gingerjs","build","app"])], cwd=base,check=True,env=my_env)
    if not debug:
        subprocess.run(["rm", "-rf", os.path.sep.join([".","","_gingerjs","__build__"])], check=True, cwd=cwd)
    # module_name = "babel"
    # module = load_module(module_name,os.path.join(dir_path,"main.py"))
    # if hasattr(module, "babel"):
    #     module.babel()
    babel_command = [
        'gingerjs',
        'babel',
    ]
    subprocess.run(babel_command, cwd=base, env=my_env)
    subprocess.run(["yarn" if package_manager == "yarn" else "npx", "webpack","--config",os.path.dirname(__file__)+os.sep+"webpack.config.js", "--stats-error-details"], cwd=base, check=True, env=my_env)
    
    for dirpath, _, filenames in os.walk(os.path.join(base,"public","templates")):
        for filename in filenames:
            if filename != "layout.html":
                # Construct the source and destination paths
                source_path = os.path.join(base, 'public', 'templates', filename)
                destination_path = os.path.join(base,"_gingerjs", 'build', 'templates', filename)

                # Create the destination directory if it does not exist
                os.makedirs(os.path.dirname(destination_path), exist_ok=True)

                # Copy the file
                shutil.copyfile(source_path, destination_path)
                

    if not os.path.exists(os.path.join(base,"public","static")):
        os.makedirs(os.path.join(base,"public","static"),exist_ok=True)

    # Construct the source and destination paths
    source_path = os.path.join(base, 'public', 'static')
    destination_path = os.path.join(base, '_gingerjs', 'build', 'static')

    

    # Iterate through the source directory
    for root, dirs, files in os.walk(source_path):
        for name in dirs:
            src_dir = os.path.join(root, name)
            dest_dir = os.path.join(destination_path, os.path.relpath(src_dir, source_path))
            copy_if_not_exists(src_dir, dest_dir)
        for name in files:
            src_file = os.path.join(root, name)
            dest_file = os.path.join(destination_path, os.path.relpath(src_file, source_path))
            copy_if_not_exists(src_file, dest_file)

