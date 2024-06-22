const fs = require("fs");
const path = require("path");
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');

let  entry = [
  path.resolve(__dirname, "build", "app", "main.js")
]

const MODE = "development"

if(fs.existsSync(path.resolve(__dirname, "src","global.css"))){
  entry = [
    path.resolve(__dirname, "build", "app", "main.js"),
    path.resolve(__dirname, "src", "global.css")
  ] 
}

const entry_output = {
  mode: "development",
  entry: entry,
  output: {
    path: path.resolve(__dirname, "public", "static"),
    filename: 
      MODE === "development"
      ? path.join("./","js","[name].buundle.js")
      : path.join("./","js","[name].[contenthash].js"),
    publicPath: "/static"
  }
}

const config = {
  ...entry_output,
  optimization: {
    splitChunks: {
      cacheGroups: {
        commons: {
          chunks: "all",
          test: /[\\/]node_modules[\\/]/,
          name: __dirname.split("/")[__dirname.split("/").length - 1].split(" ").join("")
        }
      }
    }
  },
  stats: {
    assets: true
  },
  module: {
    rules: [
      {
        test: /\.(jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader",
          options: {
            presets: ["@babel/preset-env", "@babel/preset-react"],
          },
        },
      },
      {
        test: /\.css$/i,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          'postcss-loader',
        ],
      },
    ],
  },
  plugins: [
    new MiniCssExtractPlugin({
      // filename: 'global.css', needs to be relative to output
      filename :path.join("./", "css", "[name].css"),
      chunkFilename:path.join("./", "css", "[id].css")
    }),
    new HtmlWebpackPlugin({
      template: path.join(__dirname,"public","templates","layout.html"),
      filename :path.join("../../", "build","templates", "layout.html"),
      scriptLoading: "defer"
    }),
  ],
 
  resolve: {
    extensions: [".js", ".jsx"], // Add other extensions as needed
  },
}

module.exports = config;
