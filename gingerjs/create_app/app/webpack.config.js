const path = require("path");
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const createApp = require("gingerjs/createApp");

module.exports = {
  mode: "development",
  entry: createApp(__dirname,true),
  output: {
    path: path.resolve(__dirname, "public", "static", "js"),
    filename: "app.js",
    libraryTarget: "umd",
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
      filename :path.join("../", "css","global.css"),
    }),
  ],
 
  resolve: {
    extensions: [".js", ".jsx"], // Add other extensions as needed
  },
};
