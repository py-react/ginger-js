const path = require("path");
const fs = require("fs");
const { transform } = require("@svgr/core");
const babel = require("@babel/core");


const load_svg = function (source) {
  //   const options = this.getOptions();
  // Use a regular expression to find and replace the SVG path
  const updatedSource = source.replace(
    /require\(["'](.*?)\/(.*?).svg["']\)/g,
    (match, p1, p2) => {
      const svgPath = path
        .join(path.dirname(this.resourcePath), p1, p2)
        .replace(["","_gingerjs","build",""].join(path.sep), ["","src",""].join(path.sep));
      
      const ext = ".svg";
      const d = fs.readFileSync(svgPath + ext, "utf8");
      const jsxCode = transform.sync(
        d,
        {
          plugins: [
            "@svgr/plugin-svgo",
            "@svgr/plugin-jsx",
            "@svgr/plugin-prettier",
          ],
        },
        {
          filePath: p2,
        }
      );
      if (!fs.existsSync(path.dirname(svgPath.replace(["","src",""].join(path.sep),["","_gingerjs","build",""].join(path.sep)) + ".js"))) {
        fs.mkdirSync(path.dirname(svgPath.replace(["","src",""].join(path.sep),["","_gingerjs","build",""].join(path.sep)) + ".js"), { recursive: true });
      }
      // Compile JSX to JS using Babel
      const { code: compiledJsxCode } = babel.transformSync(jsxCode, {
        presets: ["@babel/preset-env", "@babel/preset-react"],
      });
      fs.writeFileSync(svgPath.replace(["","src",""].join(path.sep),["","_gingerjs","build",""].join(path.sep)) + ".js", compiledJsxCode);
      return `require("${svgPath.replace(["","src",""].join(path.sep),["","_gingerjs","build",""].join(path.sep)) + ".js"}")`;
    }
  );
  fs.writeFileSync(this.resourcePath, updatedSource);
  // Return the updated source
  return updatedSource;
};

module.exports = load_svg
