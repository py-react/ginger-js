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
    # Define the regex pattern to match any text within square brackets
    pattern = re.compile(r"\[([^\]]+)\]")
    # Replace the matching segments with : followed by the captured text
    return pattern.sub(r":\1", path)

def create_routes(data, parent_path="/", layout=DEFAULT_LAYOUT, debug=False):
    routes = []
    parent = parent_path
    layout_comp = layout
    page_not_found = PAGE_NOT_FOUND
    print({"data":data},"findMe")
    # TODO :get 404 page and other
    if "layout.jsx" in data:
        layout_comp = generate_component_name(data["layout.jsx"])
    else:
        layout_comp = DEFAULT_LAYOUT

    if "not_found.jsx" in data:
        page_not_found = generate_component_name(data["not_found.jsx"])

    if "index.jsx" in data:
        routes.append(f'<Route path="{replace_wildcards(parent)}" element={{<{layout_comp}/>}} >')
        for key in data:
            route_path = data["index.jsx"].split("app")[1].replace("/index.jsx", "")
            if key not in {"index.jsx", "layout.jsx", "app.jsx", "loading.jsx","not_found.jsx"}:
                routes.extend(create_routes(data[key], key, layout_comp, debug))
            elif key not in {"layout.jsx", "app.jsx", "loading.jsx","not_found.jsx"}:
                component_name = generate_component_name(data["index.jsx"])
                add_path = f'path="{replace_wildcards(route_path).replace(f"/{parent}", "")}"'
                sub_paths = route_path.split("/")
                with open(data["index.jsx"], "r") as file:
                    file_data = file.read()
                if "use client" in file_data:
                    routes.append(f'''
                            <Route 
                                {
                                    "index" if sub_paths[-1] == parent_path or route_path in {"", "/src/"} else add_path
                                }  
                                element={{
                                    <LazyComp 
                                        LazyComponent={component_name} 
                                        Loader={{typeof {component_name.replace("Index", "Loading")}==='function'?{component_name.replace("Index", "Loading")}:<div style={{height:"100vh"}} className="flex  w-full justify-center items-center"><h3>loading...</h3></div>}} 
                                        {{...props}}
                                    />
                                }}
                            />
                        ''')
                else:
                    routes.append(f'''
                        <Route {"index" if sub_paths[-1] == parent_path or route_path in ["", "/src/"] else add_path}
                            element={{
                                    <React.Suspense fallback={{typeof {component_name.replace("Index","Loading")} === "function"?<{component_name.replace("Index","Loading")}/>: <div style={{{{ height: "100vh" }}}} className="flex w-full justify-center items-center"><h3>loading...</h3></div>}}>
                                        <{component_name} {{...props}} />
                                    </React.Suspense>
                            }}
                        />
                    ''')

        routes.append(f'<Route path="*" element={{<{page_not_found} />}}/>')
        routes.append('</Route>')
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
                    <h1 style={{
                            fontSize: "8rem",
                            lineHeight: "1",
                            color: "rgb(17 24 39)"
                        }} className="font-bold text-gray-900 dark:text-gray-50">404</h1>
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

    const ErrorMessage = ({ serverProps:{hasError,error},...props }) => {
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
        const LazyIndex = shouldRenderLazy ? <LazyComponent {{...props}} /> : <div style={{{{height:"100vh"}}}} className="flex w-full justify-center items-center"><h3>loading...</h3></div>;

        return (
            <>
                {{shouldRenderLazy && (
                    <React.Suspense fallback={{<Loader />}}>
                        <{error_component}> 
                            <LazyIndex />
                        </{error_component_closing}> 
                    </React.Suspense>
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
            console.log('ErrorBoundary')
            this.state = { hasError: false};
        }

        static getDerivedStateFromError(error) {
            console.log({ error },'findMe')
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
                if "use client" in file_data:
                    imports.append(f'const {component_name} = React.lazy(() => import("{node.replace("/src/", "/build/").replace(".jsx", ".js")}"));')
                else:
                    imports.append(f'import {component_name} from "{node.replace("/src/", "/build/").replace(".jsx", ".js")}";')
        else:
            for key in node:
                traverse(node[key], f'{path}/{key}')

    traverse(obj, "")
    print({"imports":imports})
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
        import React, {{ useState, useEffect }} from 'react';
        {'import Error from "./Error"' if debug else ""}
        import GenericNotFound from "./GenericNotFound"   
        import {{ BrowserRouter as Router, Route, Routes, Outlet }} from 'react-router-dom';     
        import {{ Redirect }} from 'react-router'
        function DefaultLayout_() {{
            return <Outlet />
        }}

        {generate_import_statements(node_data)}

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
    import React from 'react';
    import Router from "./BrowserRouterWrapper"
    import { hydrateRoot } from 'react-dom/client';
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
                delete window.flask_react_app_props
                document.getElementById("serverScript")?.remove();
                return { serverProps: data, ...props };
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

    const container = document.getElementById("root");
    hydrateRoot(container, <Router><App {...getServerProps({})}/></Router>,{onRecoverableError:handleHydrationError});
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

    build_cra = subprocess.Popen(["yarn", "babel", "--extensions", ".js,.jsx", "./__build__", "-d", "./build/app"], cwd=base,stdout=subprocess.PIPE)
    build_cra_com = build_cra.communicate()
    logger.debug(build_cra_com[0].decode("utf-8"))
    if build_cra_com[1]:
        logger.error(build_cra_com[1].decode("utf-8"))
    if not debug:
        subprocess.run(["rm", "-rf", "./__build__"], check=True,cwd=cwd)
    babel_command = [
        'gingerjs',
        'babel',
    ]
    babe_build = subprocess.Popen(babel_command, cwd=base, env=my_env,stdout=subprocess.PIPE)
    babe_build_com = babe_build.communicate()
    logger.debug(babe_build_com[0].decode("utf-8"))
    if babe_build_com[1]:
        logger.error(babe_build_com[1].decode("utf-8"))

    webpack_build = subprocess.Popen(["yarn", "webpack", "--stats-error-details"], cwd=base, env=my_env,stdout=subprocess.PIPE)
    webpack_build_com = webpack_build.communicate()
    logger.debug(webpack_build_com[0].decode("utf-8"))
    if webpack_build_com[1]:
        logger.error(webpack_build_com[1].decode("utf-8"))
    
    


create_app()