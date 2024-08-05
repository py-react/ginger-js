const fs = require("fs");
const path = require("path");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const HtmlWebpackPlugin = require("html-webpack-plugin");

// {
//   react: "react-dom", "react-icons", "react-router";
//   redux: "redux",
//     "react-redux",
//     "@reduxjs",
//     "redux-sentry-middleware",
//     "addon-redux";
//   phone: "react-phone-number-input", "libphonenumber-js", "country-flag-icons";
//   analytics: "@segment", "@datadog";
//   search: "@findhotel/sapi", "algoliasearch";
//   experimentation: "@optimizely", "opticks";
//   intl: "@formatjs", "intl-messageformat";
//   aws: "@aws-amplify", "aws-amplify", "@aws-sdk", "@aws-crypto";
//   fp: "ramda/es", "immer";
// }

const getNodeModulesRegExp = (deps) =>
  new RegExp(`[\\/]node_modules[\\/]${deps.join("|")}`);

const excludeNodeModulesRegExp = (deps) =>
  new RegExp(`[\\/]node_modules[\\/](?!(${deps.join("|")})).*`);

const muiCacheGroupDeps = ["@mui", "@emotion", "mui"];
const stylesCacheGroupDeps = [
  "styled-componenents",
  "radix-ui",
  "css-",
  "lucide-react",
  "floating-ui",
];
const reactCacheGroupDeps = [
  "react",
  "react-dom",
  "react-icons",
  "react-router",
];
const reduxCacheGroupDeps = [
  "redux",
  "react-redux",
  "@reduxjs",
  "redux-sentry-middleware",
  "addon-redux",
  "reselect",
];

const phoneCacheGroupDeps = [
  "react-phone-number-input",
  "libphonenumber-js",
  "country-flag-icons",
];

const monitoringCacheGroupDeps = ["@segment", "@datadog"];
const searchCacheGroupDeps = ["@findhotel/sapi", "algoliasearch"];
const experimentationCacheGroupDeps = ["@optimizely", "opticks"];
const intlCacheGroupDeps = ["@formatjs", "intl-formatmessage"];
const awsCacheGroupDeps = [
  "@aws-amplify",
  "aws-amplify",
  "@aws-sdk",
  "@aws-crypto",
];

const fpCacheGroupDeps = ["ramda/es", "immer"];

const MUICacheGroup = {
  name: "MUI",
  filename: "[name].[contenthash].bundle.js",
  enforce: true,
  test: getNodeModulesRegExp(muiCacheGroupDeps),
  reuseExistingChunk: true,
};

const StylesCacheGroup = {
  name: "css_in_js",
  filename: "[name].[contenthash].bundle.js",
  enforce: true,
  test: getNodeModulesRegExp(stylesCacheGroupDeps),
  reuseExistingChunk: true,
};

const ReactCacheGroup = {
  name: "react",
  filename: "[name].[contenthash].bundle.js",
  enforce: true,
  test: getNodeModulesRegExp(reactCacheGroupDeps),
  reuseExistingChunk: true,
};

const ReduxCacheGroup = {
  name: "redux",
  filename: "[name].[contenthash].bundle.js",
  test: getNodeModulesRegExp(reduxCacheGroupDeps),
  enforce: true,
  reuseExistingChunk: true,
};

const PhoneCacheGroup = {
  name: "phone",
  filename: "[name].[contenthash].bundle.js",
  test: getNodeModulesRegExp(phoneCacheGroupDeps),
  enforce: true,
  reuseExistingChunk: true,
};

const MonitoringCacheGroup = {
  name: "monitoring",
  filename: "[name].[contenthash].bundle.js",
  enforce: true,
  test: getNodeModulesRegExp(monitoringCacheGroupDeps),
  reuseExistingChunk: true,
};

const SearchCacheGroup = {
  name: "search-apiv",
  filename: "[name].[contenthash].bundle.js",
  enforce: true,
  test: getNodeModulesRegExp(searchCacheGroupDeps),
  reuseExistingChunk: true,
};

const ExperimentationCacheGroup = {
  name: "experimentation",
  filename: "[name].[contenthash].bundle.js",
  enforce: true,
  test: getNodeModulesRegExp(experimentationCacheGroupDeps),
  reuseExistingChunk: true,
};

const IntlCacheGroup = {
  name: "intl",
  filename: "[name].[contenthash].bundle.js",
  enforce: true,
  test: getNodeModulesRegExp(intlCacheGroupDeps),
  reuseExistingChunk: true,
};

const AWSCacheGroup = {
  name: "aws",
  filename: "[name].[contenthash].bundle.js",
  test: getNodeModulesRegExp(awsCacheGroupDeps),
  enforce: true,
  reuseExistingChunk: true,
};

const FPCacheGroup = {
  name: "fp",
  filename: "[name].[contenthash].bundle.js",
  test: getNodeModulesRegExp(fpCacheGroupDeps),
  enforce: true,
  reuseExistingChunk: true,
};

const vendorCacheGroupDeps = [
  ...reactCacheGroupDeps,
  ...reduxCacheGroupDeps,
  ...phoneCacheGroupDeps,
  ...monitoringCacheGroupDeps,
  ...searchCacheGroupDeps,
  ...experimentationCacheGroupDeps,
  ...intlCacheGroupDeps,
  ...awsCacheGroupDeps,
  ...fpCacheGroupDeps,
  ...stylesCacheGroupDeps,
  ...muiCacheGroupDeps,
];

const VendorCacheGroup = {
  name: "vendor",
  filename: "[name].[contenthash].bundle.js",
  test: excludeNodeModulesRegExp(vendorCacheGroupDeps),
  enforce: true,
  reuseExistingChunk: true,
};

const cacheGroups = {
  styles: StylesCacheGroup,
  mui: MUICacheGroup,
  react: ReactCacheGroup,
  redux: ReduxCacheGroup,
  phone: PhoneCacheGroup,
  monitoring: MonitoringCacheGroup,
  search: SearchCacheGroup,
  experimentation: ExperimentationCacheGroup,
  intl: IntlCacheGroup,
  aws: AWSCacheGroup,
  fp: FPCacheGroup,
  vendor: VendorCacheGroup,
};

const splitChunks = {
  chunks: "all",
  cacheGroups: {
    defaultVendors: false,
    [cacheGroups.styles.name]: cacheGroups.styles,
    [cacheGroups.mui.name]: cacheGroups.mui,
    [cacheGroups.react.name]: cacheGroups.react,
    [cacheGroups.redux.name]: cacheGroups.redux,
    [cacheGroups.phone.name]: cacheGroups.phone,
    [cacheGroups.monitoring.name]: cacheGroups.monitoring,
    [cacheGroups.search.name]: cacheGroups.search,
    [cacheGroups.experimentation.name]: cacheGroups.experimentation,
    [cacheGroups.intl.name]: cacheGroups.intl,
    [cacheGroups.aws.name]: cacheGroups.aws,
    [cacheGroups.fp.name]: cacheGroups.fp,
    vendor: cacheGroups.vendor,
    default: {
      minChunks: 2,
      priority: -20,
      reuseExistingChunk: true,
    },
  },
};

let entry = [path.resolve(process.cwd(), "_gingerjs","build", "app", "main.js")];
const STATIC_SITE = process.env.STATIC_SITE === "True"?true:false;
const TYPESCRIPT = process.env.TYPESCRIPT === "True"?true:false;
const MODE = process.env.DEBUG==="True"?"development":"production";
const MAIN_HTML = STATIC_SITE?"index.html": "layout.html"
const TAILWIND = process.env.TAILWIND === "True"?true:false;
const static_path =  "/static"

if (fs.existsSync(path.resolve(process.cwd(), "src", "global.css"))) {
  entry = [
    path.resolve(process.cwd(), "_gingerjs","build", "app", "main.js"),
    path.resolve(process.cwd(), "src", "global.css"),
  ];
}

const rules = (TYPESCRIPT?[
  {
    test: /\.((js|jsx|ts|tsx))$/,
    exclude: /node_modules/,
    use: [
      {
        loader: path.resolve(__dirname, 'svgr-loader.js'),
      },
      {
        loader: "babel-loader",
        options: {
          presets: ["@babel/preset-env", "@babel/preset-react"],
        },
      },
    ],
  },
  
  
]:[
  {
    test: /\.((js|jsx))$/,
    exclude: /node_modules/,
    use: [
      {
        loader: path.resolve(__dirname, 'svgr-loader.js'),
      },
      {
        loader: "babel-loader",
        options: {
          presets: ["@babel/preset-env", "@babel/preset-react"],
        },
      },
    ],
  },
])

const entry_output = {
  context: process.cwd(),
  mode: MODE,
  entry: entry,
  output: {
    path: path.resolve(process.cwd(), "_gingerjs", "build", "static"),
    filename:
      MODE === "development"
        ? path.join("."+path.sep, "js", "[name].js")
        : path.join("."+path.sep, "js", "[name].[contenthash:8].js"),
    chunkFilename:
      MODE === "development"
        ? path.join("."+path.sep, "js", "[name].js")
        : path.join("."+path.sep, "js", "[name].[contenthash:8].js"),
    library: "[name]",
    publicPath: static_path,
    clean: true,
  },
};

if(STATIC_SITE){
  entry_output.devServer= {
    static: {
      directory: path.resolve(process.cwd(), "_gingerjs", "build"),
    },
    historyApiFallback: true,
    hot: true,
    compress: true,
    port: process.env.PORT||5001,
    client: {
      logging: 'info',
      overlay: {
        errors:true,
        runtimeErrors: true,
      }
    },
  }
}

const config = {
  ...entry_output,
  devtool: MODE === "development" ? "source-map" : false,
  optimization: {
    splitChunks: {
      minSize: 17000,
      minRemainingSize: 0,
      minChunks: 1,
      maxAsyncRequests: 30,
      maxInitialRequests: 30,
      automaticNameDelimiter: "_",
      enforceSizeThreshold: 30000,
      ...splitChunks,
    },
  },
  module: {
    rules: [
      ...rules,
      {
        test: /\.(css)$/i,
        use: [MiniCssExtractPlugin.loader, ...(TAILWIND ?["css-loader", "postcss-loader"]:["css-loader"])],
      },
    ],
  },
  plugins: [
    // new ChunksWebpackPlugin(),
    new MiniCssExtractPlugin({
      // filename: 'global.css', needs to be relative to output
      filename: path.join("."+path.sep, "css", "[name].css"),
      chunkFilename: path.join("."+path.sep, "css", "[id].css"),
    }),
    new HtmlWebpackPlugin({
      template: path.join(process.cwd(), "public", "templates", MAIN_HTML),
      filename: path.join(".."+path.sep, "templates", MAIN_HTML),
    }),
  ],

  resolve: {
    extensions: [".js", ".jsx",".ts",".tsx"], // Add other extensions as needed
  },
};

module.exports = config;
