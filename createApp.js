const path = require("path");
const fs = require("fs");
const { execSync } = require("child_process");

// Function to recursively search for JSX files and create a list of absolute paths
function findJSXFiles(directoryPath, jsxFilesList = []) {
  const files = fs.readdirSync(directoryPath);

  files.forEach((file) => {
    const filePath = path.join(directoryPath, file);
    const stat = fs.statSync(filePath);

    if (stat.isDirectory()) {
      // Recursively search in subdirectories
      findJSXFiles(filePath, jsxFilesList);
    } else if (path.extname(file) === ".jsx") {
      // If the file has a .jsx extension, add its absolute path to the list
      jsxFilesList.push(filePath);
    }
  });

  return jsxFilesList;
}

const DEFAULT_LAYOUT = "DefaultLayout_";

function replaceWildcardsInComponentName(path) {
  // Define the regex pattern to match any text within square brackets
  const pattern = /\[([^\]]+)\]/g;

  // Replace the matching segments with : followed by the captured text
  return path.replace(pattern, "_$1_");
}

function generateComponentName(componentPath) {
  const toReturn = replaceWildcardsInComponentName(
    componentPath
      .split("/")
      .slice(3)
      .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
      .join("_")
      .replace(".jsx", "")
  );
  return toReturn;
}

function replaceWildcards(path) {
  // Define the regex pattern to match any text within square brackets
  const pattern = /\[([^\]]+)\]/g;

  // Replace the matching segments with : followed by the captured text
  return path.replace(pattern, ":$1");
}

function createRoutes(data, parentPath = "/", layout = DEFAULT_LAYOUT) {
  const routes = [];
  const parent = parentPath;
  let layoutComp = layout;
  if ("layout.jsx" in data) {
    layoutComp = generateComponentName(data["layout.jsx"]);
  } else {
    layoutComp = DEFAULT_LAYOUT;
  }
  if ("index.jsx" in data) {
    routes.push(
      `<Route path="${replaceWildcards(parent)}" element={<${layoutComp}/>} >`
    );
    for (const key in data) {
      const routePath = data["index.jsx"]
        .split("app")[1]
        .replace("/index.jsx", "");
      if (
        key !== "index.jsx" &&
        key !== "layout.jsx" &&
        key !== "app.jsx" &&
        key !== "loading.jsx"
      ) {
        routes.push(...createRoutes(data[key], key, layoutComp));
      } else if (
        key !== "layout.jsx" &&
        key !== "app.jsx" &&
        key !== "loading.jsx"
      ) {
        const componentName = generateComponentName(data["index.jsx"]);
        let addPath = `path="${replaceWildcards(routePath).replace(
          `/${parent}`,
          ""
        )}"`;
        const subPaths = routePath.split("/");

        const fileData = fs.readFileSync(data["index.jsx"], "utf-8");
        if (fileData.includes("use client")) {
          routes.push(
            `<Route 
                ${
                  subPaths[subPaths.length - 1] === parentPath ||
                  routePath === ""
                    ? "index"
                    : addPath
                }  
                element={
                      <LazyComp 
                        lazyComp={${componentName}} 
                        Loader={typeof ${componentName.replace(
                          "Index",
                          "Loading"
                        )}==='function'?${componentName.replace(
              "Index",
              "Loading"
            )}:<div>Loading...</div>} 
                        {...props}
                      />
            }/>`
          );
        } else {
          routes.push(
            `<Route ${
              subPaths[subPaths.length - 1] === parentPath || routePath === ""
                ? "index"
                : addPath
            }  element={
              <React.Suspense fallback={typeof ${componentName.replace(
                "Index",
                "Loading"
              )}==='function'?<${componentName.replace(
              "Index",
              "Loading"
            )} />:<div>Loading...</div>}>
                <${componentName} {...props}/>
              </React.Suspense>
            }/>`
          );
        }
      }
    }
    routes.push(`</Route>`);
  }
  return routes;
}

function generateLazyComponent() {
  // Placeholder component for server-side rendering
  return `
    const LazyComp = ({lazyComp,Loader,...props}) => {
      // State to track whether to render the lazy component
      const [shouldRenderLazy, setShouldRenderLazy] = useState(false);

      // On the client side, enable rendering of the lazy component
      useEffect(() => {
        setShouldRenderLazy(true);
      }, []);

      // Lazy load the component only on the client side
      const LazyIndex = shouldRenderLazy ? lazyComp : React.createElement("div","Loading...");

      return (
        <>
          {shouldRenderLazy && (
            <React.Suspense fallback={<Loader />}>
              <LazyIndex {...props}/>
            </React.Suspense>
          )}
        </>
      );
    };
  `;
}

function generateImportStatements(obj) {
  const imports = [];
  function traverse(node, path) {
    if (typeof node === "string") {
      const componentName = generateComponentName(node);
      if (!node.includes("/app.jsx")) {
        fileDate = fs.readFileSync(`${node}`, "utf-8");
        if (fileDate.includes("use client")) {
          imports.push(
            `const ${componentName} = React.lazy(()=>import('${node
              .replace("/src/", "/build/")
              .replace(".jsx", ".js")}'));`
          );
        } else {
          imports.push(
            `import ${componentName} from '${node
              .replace("/src/", "/build/")
              .replace(".jsx", ".js")}';`
          );
        }
      }
    } else {
      for (const key in node) {
        traverse(node[key], `${path}/${key}`);
      }
    }
  }

  traverse(obj, "");

  return imports.join("\n");
}

function createReactAppWithRoutes(paths) {
  function createNodes(componentsPaths, nodes = {}) {
    for (let j = 0; j < componentsPaths.length; j++) {
      let relativePath = componentsPaths[j].split("src")[1];
      let paths = relativePath.split("/").filter(Boolean); // Remove empty strings from split
      let current = nodes;
      for (let i = 0; i < paths.length - 1; i++) {
        let key = paths[i];
        if (!current[key]) {
          current[key] = {};
        }
        current = current[key];
      }
      current[paths[paths.length - 1]] = componentsPaths[j];
    }
    return nodes;
  }
  const nodeData = createNodes(paths);

  // Generate the React router code dynamically
  return `
    import React,{useState,useEffect} from 'react';
  
    import { BrowserRouter as Router, Route, Routes, Outlet } from 'react-router-dom';
  
    ${generateImportStatements(nodeData)}
  
    function DefaultLayout_(){
      return <Outlet />
    }
  
    ${generateLazyComponent()}
    
    function App(props) {
        return (
            <Routes>
                ${createRoutes(nodeData["app"]).join("\n")}
            </Routes>
        );
    }
    export default App
    `;
}

function generateMainClientEntry() {
  return `
      import React from 'react';
      import Router from "./BrowserRouterWrapper"
      import { hydrateRoot } from 'react-dom/client';
      import App from "./app"
      function getServerProps(props) {
        try {
          if (window !== undefined) {
            const data  = JSON.parse(JSON.stringify(window.flask_react_app_props))
            delete window.flask_react_app_props
            document.getElementById("serverScript")?.remove();
            return { serverProps: data, ...props };
          }
        } catch (error) {
          // pass
        }
        return props;
      }
  
  
      const container = document.getElementById("root");
      hydrateRoot(container, <Router><App {...getServerProps({})}/></Router>);
    `;
}

function generateBrowserRouterWrapper() {
  return `
      import React from 'react';
      import { BrowserRouter } from 'react-router-dom';
  
      function Router({children}){
        return (
          <BrowserRouter>{children}</BrowserRouter>
        )
      }
  
      export default Router
    `;
}
function generateStaticRouterWrapper() {
  return `
      import React from 'react';
      import { StaticRouter } from "react-router-dom/server";
  
      function Router({children,url}){
        return (
          <StaticRouter location={url}>{children}</StaticRouter>
        )
      }
  
      export default Router
    `;
}

const createApp = () => {
  try {
    execSync("rm -rf ./build");
    execSync("rm -rf ./__build__");
    execSync("rm ./public/static/js/app.js");
  } catch (error) {
    // pass
  }

  fs.mkdirSync(path.resolve(__dirname, "__build__"), { recursive: true });

  fs.writeFileSync(
    path.resolve(__dirname, "__build__", "app.jsx"),
    createReactAppWithRoutes(
      findJSXFiles(path.resolve(__dirname, "src", "app"))
    )
  );
  fs.writeFileSync(
    path.resolve(__dirname, "__build__", "BrowserRouterWrapper.jsx"),
    generateBrowserRouterWrapper()
  );
  fs.writeFileSync(
    path.resolve(__dirname, "__build__", "StaticRouterWrapper.jsx"),
    generateStaticRouterWrapper()
  );
  fs.writeFileSync(
    path.resolve(__dirname, "__build__", "main.jsx"),
    generateMainClientEntry()
  );

  execSync("babel --extensions .js,.jsx ./__build__ -d ./build/app");
  execSync("yarn build:babel");

  try {
    execSync("rm -rf ./__build__");
  } catch (error) {
    // pass
  }
  return path.resolve(__dirname, "build", "app", "main.js");
};

module.exports = {
  createApp,
};
