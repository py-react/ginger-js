const { Writable } = require("stream");
const path = require("path");
const ext = "js";

const React = require("react");
const ReactDOMServer = require("react-dom/server");

// Custom writable stream that logs data to the console
class LoggingWritableStream extends Writable {
  constructor(options) {
    super(options);
    this.data = [];
  }

  renderString() {
    return this.data.join("");
  }

  _write(chunk, encoding, callback) {
    this.data.push(chunk.toString());
    // Call the callback to signal that the chunk has been processed
    callback();
  }
}

class SSR {
  constructor(props) {
    this.props = JSON.parse(props);
  }
  render() {
    const App = require(path.resolve("./", "build", "app", "app.js"));
    const StaticRouter = require(path.resolve(
      "./",
      "build",
      "app",
      "StaticRouterWrapper.js"
    ));
    const { location } = this.props;
    const ReactElement = React.createElement(App.default, {
      children: null,
      location,
      serverProps: this.props,
    });
    const StaticRouterWrapper = React.createElement(StaticRouter.default, {
      children: ReactElement,
      url: this.props.location.path,
    });
    const componentHTML =
      ReactDOMServer.renderToPipeableStream(StaticRouterWrapper);

    // Create an instance of the logging writable stream
    const loggingWritableStream = new LoggingWritableStream();
    componentHTML.pipe(loggingWritableStream);
    // After the stream has ended, the concatenated string can be accessed
    loggingWritableStream.on("finish", () => {
      console.log(loggingWritableStream.renderString()); //
    });
  }

  createElement(path, props) {
    const componentFile = require(path);
    const Component = componentFile.default; // Import the individual component
    const reactElem = React.createElement(Component, {
      ...props,
    });
    return reactElem;
  }
}

(async () => {
  try {
    const props = process.argv[2] || JSON.stringify({location:{path: "/",baseUrl:"/",query:""}});
    const ssr = new SSR(props);
    ssr.render();
  } catch (error) {
    console.error("Error:", error);
    process.exit(1);
  }
})();
