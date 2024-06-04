const fs = require("fs");
const path = require("path");
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

let  entry = [path.resolve(__dirname, "build", "app", "main.js")]

if(fs.existsSync(path.resolve(__dirname, "src","global.css"))){
  entry = [path.resolve(__dirname, "build", "app", "main.js"),path.resolve(__dirname, "src", "global.css")] 
}

const entry_output = {
  mode: "development",
  entry: entry,
  output: {
    path: path.resolve(__dirname, "public", "static", "js"),
    filename: "app.js",
    libraryTarget: "umd",
  }
}

const config = {
  ...entry_output,
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
      filename :path.join("../", "css","global.css"),
    }),
  ],
 
  resolve: {
    extensions: [".js", ".jsx"], // Add other extensions as needed
  },
}

module.exports = config;
