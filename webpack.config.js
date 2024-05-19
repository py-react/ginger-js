const path = require("path");
const { createApp } = require("./createApp");

module.exports = {
  entry: createApp(),
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
    ],
  },
  mode: "development",
  resolve: {
    extensions: [".js", ".jsx"], // Add other extensions as needed
    alias: {
      src: path.resolve(__dirname, "src"), // Alias for the components directory
      components: path.resolve(__dirname, "src", "components"), // Alias for the components directory
    },
  },
};
