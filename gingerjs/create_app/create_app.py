import os
import re
import subprocess

class Logger():
    def __init__(self, name):
        self.name = name
    
    def debug(self, *args, **kwargs):
        if os.environ.get("DEBUG") == "true" or False:
            print(*args, **kwargs)
    
    def info(self, *args, **kwargs):
        print(*args, **kwargs)
    
    def error(self, *args, **kwargs):
        print(*args, **kwargs)

logger = Logger("create-react-app")
DEFAULT_LAYOUT = "DefaultLayout_"
PAGE_NOT_FOUND = "GenericNotFound"
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
    loader = 'DefaultLoader_' if  parentLoader=="" else parentLoader
    full_parent_path = last_path + "/" + replace_wildcards(parent).replace('*','') if replace_wildcards(parent) != "*" else last_path  + replace_wildcards(parent).replace('*','')
    layout_comp = DEFAULT_LAYOUT
    page_not_found = None

    # TODO :get 404 page and other
    if "layout.jsx" in data:
        layout_comp = generate_component_name(data["layout.jsx"])
    elif "layout.jsx" not in data and parent_path == "/":
        layout_comp = DEFAULT_LAYOUT

    if "not_found.jsx" in data:
        page_not_found = generate_component_name(data["not_found.jsx"])

    if "loading.jsx" in data:
        loader = generate_component_name(data["loading.jsx"])

    if "index.jsx" in data:
        routes.append(f"""
                <Route path="{replace_wildcards(parent)}" 
                    element = {{
                        <LayoutPropsProvider forUrl={{"{full_parent_path+"/"}"}} Element = {{{layout_comp}}}  {{...props}}/>
                    }}
                    
                >
        """)
        for key in data:
            route_path = data["index.jsx"].split("app")[1].replace("/index.jsx", "")
            if key not in {"index.jsx", "layout.jsx", "app.jsx", "loading.jsx","not_found.jsx"}:
                routes.extend(create_routes(data[key], key, full_parent_path,loader, debug))
            elif key not in {"layout.jsx", "app.jsx", "loading.jsx","not_found.jsx"}:
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
            if "/app.jsx" not in node:
                file_data = open(node, "r").read()
                # if "use client" in file_data:
                imports.append(f"""const {component_name} = React.lazy(() => import('{node.replace("/src/", "/build/").replace(".jsx", ".js")}'));""")
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
            paths = list(filter(None, relative_path.split("/")))  # Remove empty strings from split
            current = nodes
            for i in range(len(paths) - 1):
                key = paths[i]
                current = current.setdefault(key, {})
            current[paths[-1]] = component_path
        return nodes

    node_data = create_nodes(paths)
    to_return = [
        f"""
        import React, {{ useState, useEffect,useRef }} from 'react';
        {'import Error from "./Error"' if debug else ""}
        import GenericNotFound from "./GenericNotFound"   
        import {{ BrowserRouter as Router, Route, Routes, Outlet, useLocation }} from 'react-router-dom';     
        import {{ Redirect, matchPath }} from 'react-router';

        {generate_import_statements(node_data)}
        

        const DefaultLayout_ = React.memo(()=>{{
            return <Outlet/>
        }})

        const DefaultLoader_ = React.memo(()=>{{
            return <div
                style={{{{
                    height: "100vh",
                    display: 'flex',
                    width: '100%',
                    justifyContent: 'center',
                    alignItems: 'center',
                    gap: '1rem',
                }}}}
              >
                <div style={{{{
                    backgroundColor: 'gray',
                    width: '20px',
                    height: '20px',
                    borderRadius: '0.375rem',
                    animation: 'bounce 1s ease-in-out 0s infinite'
                }}}} />
                <div style={{{{
                    backgroundColor: 'gray',
                    width: '20px',
                    height: '20px',
                    borderRadius: '0.375rem',
                    animation: 'bounce 1s ease-in-out 0.2s infinite'
                }}}} />
                <div style={{{{
                    backgroundColor: 'gray',
                    width: '20px',
                    height: '20px',
                    borderRadius: '0.375rem',
                    animation: 'bounce 1s ease-in-out 0.4s infinite'
                }}}} />
              </div>
        }})

        const PropsProvider = React.memo(({{Element,Fallback,...props}})=>{{
            const [propsData,setPropData] = useState({{...props}})
            const [loading,setLoading] = useState(true)

            useEffect(()=>{{
                const data  = JSON.parse(JSON.stringify(window.flask_react_app_props))
                setPropData(data)
                setLoading(false)
                window.__enableScroll__()
            }},[])
            
            return (
                <React.Suspense fallback={{<Fallback />}}>
                    <Element {{...propsData}} />
                    <div style={{{{
                            padding:"1rem",
                            position: "absolute",
                            top:0,
                            left:0,
                            width:"100vw",
                            height:"100vh",
                            display:(loading && Fallback) ? "initial":"none",
                            zIndex:99999999999,
                            background:"rgb(255 255 255 / 0.5)"
                        }}}}
                    >
                        <Fallback />
                    </div>
                </React.Suspense >
            )
        }})

        const LayoutPropsProvider = React.memo(({{Element,Fallback , forUrl, ...props}})=>{{
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
        }})

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
    return '''
    import React,{useState,useEffect} from 'react';
    import Router from "./BrowserRouterWrapper"
    import ReactDOM from 'react-dom';
    import { hydrateRoot,createRoot } from 'react-dom/client';
    import App from "./app"
    function getServerProps(props) {{
        try {
            if (window !== undefined) {
                function getElementAttributeByPrefix(documentId, prefix) {
                    const element = document.getElementById(documentId);
                    if (!element) {
                        return null;
                    }
                    const toReturn = {}

                    for (const attribute of element.attributes) {
                        const attributeName = attribute.name;

                        if (attributeName.startsWith(prefix)) {
                            try {
                                toReturn[attributeName.replace(prefix, "")] = JSON.parse(attribute.value)
                            } catch {
                                toReturn[attributeName.replace(prefix, "")] = attribute.value
                            }
                            return attribute.value;
                        }
                    }

                    return toReturn;
                }
                const data  = JSON.parse(JSON.stringify(window.flask_react_app_props))
                // delete window.flask_react_app_props
                // document.getElementById("serverScript")?.remove();
                return { ...data,...props };
            }
        } catch (error) {
            // pass
        }
        return props;
    }}
    function handleHydrationError(error,errorInfo) {
        console.error('Hydration error:', {error,errorInfo});
        // Run your specific function here
        // e.g., log to a service, display a fallback UI, etc.
    }
    window.__disableScroll__ = function(){
        window.overStyle = document.body.style.overflow
        window.positionStyle = document.body.style.position
        document.body.style.overflow = 'hidden';
        document.body.style.position = 'fixed';
    
    };

    window.__enableScroll__ = function(){
        document.body.style.overflow = window.overStyle;
        document.body.style.position = window.positionStyle;
    };
   

    const container = document.getElementById("root");

    const timeOfRender = new Date()
  
    window.__REACT_HYDRATE__ = function(url){
        window.__disableScroll__()
        hydrateRoot(container,<React.StrictMode><Router><App {...getServerProps({})}/></Router></React.StrictMode>,{onRecoverableError:handleHydrationError});
    }
    window.__REACT_HYDRATE__()
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

def create_app():
    my_env = os.environ.copy()
    debug = os.environ.get("DEBUG") == "True" or False
    cwd = os.getcwd()
    if cwd is None:
        raise ValueError("Current working directory not provided")

    try:
        subprocess.run(["rm", "-rf", "./build"], check=True,cwd=cwd)
        subprocess.run(["rm", "-rf", "./__build__"], check=True,cwd=cwd)
        subprocess.run(["rm", "./public/static/js/app.js"], check=True,cwd=cwd)
    except subprocess.CalledProcessError:
        pass

    os.makedirs(os.path.join(cwd, "__build__"), exist_ok=True)

    with open(os.path.join(cwd, "__build__", "app.jsx"), "w") as file:
        file.write(create_react_app_with_routes(find_jsx_files(os.path.join(cwd, "src", "app")), debug))

    with open(os.path.join(cwd, "__build__", "BrowserRouterWrapper.jsx"), "w") as file:
        file.write(generate_browser_router_wrapper())

    with open(os.path.join(cwd, "__build__", "StaticRouterWrapper.jsx"), "w") as file:
        file.write(generate_static_router_wrapper())

    with open(os.path.join(cwd, "__build__", "main.jsx"), "w") as file:
        file.write(generate_main_client_entry())

    if debug:
        with open(os.path.join(cwd, "__build__", "Error.jsx"), "w") as file:
            file.write(generate_error_component())

    with open(os.path.join(cwd, "__build__", "GenericNotFound.jsx"), "w") as file:
        file.write(generic_not_found())

    subprocess.run(["yarn", "babel", "--extensions", ".js,.jsx", "./__build__", "-d", "./build/app"], cwd=base,check=True)
    if not debug:
        subprocess.run(["rm", "-rf", "./__build__"], check=True, cwd=cwd)
    babel_command = [
        'gingerjs',
        'babel',
    ]
    subprocess.run(babel_command, cwd=base, env=my_env)
    subprocess.run(["yarn", "webpack", "--stats-error-details"], cwd=base, check=True, env=my_env)
    


    copy_index = [
        "cp",
        "./public/templates/index.html",
        "./build/templates/index.html"
    ]
    subprocess.run(copy_index, cwd=base, check=True)

    copy_static = [
        "cp",
        "-R",
        f"{base}/public/static/",
        f"{base}/build/static/"
    ]
    subprocess.run(copy_static, cwd=base, check=True)

    for root,_,files in os.walk(f'{cwd}/build'):
        if '__init__.py' not in files:
            open(f'{root}/__init__.py', 'w+')

    
    


create_app()