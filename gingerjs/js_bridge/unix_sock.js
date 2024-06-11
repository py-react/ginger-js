const net = require("net");
const path = require("path");
const fs = require("fs");
const SSR = require("../SSR/routes");

const args = process.argv.slice(2);

function getArgValue(key, defaultValue = null) {
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith(`${key}=`)) {
      let value = args[i].slice(args[i].indexOf("=") + 1);
      return value;
    }
  }
  return defaultValue;
}

const debug = getArgValue("debug", "False")==="True"?true:false;
const debug_log = (msg) => {
  if (debug) {
    return console.log(`${process.pid} Node Bridge: `, msg);
  }
  return () => {};
};

debug_log("Running in debug mode, This setting is Not Recomeneded for production use")
const cwd = getArgValue("cwd",path.join("./"));
const ssr = new SSR(cwd);
try {
  const console_log = debug_log;

  // const args = process.argv.slice(2);
  const socketPath = getArgValue("sock_path",path.join(__dirname, `unix.sock`));
  // Remove the socket file if it already exists
  if (fs.existsSync(socketPath)) {
    try {
      // pass just a wait time
    } catch (error) {
      console.error(`Error removing socket file: ${err.message}`);
      process.exit(1);
    }
    return;
  }


  const server = net.createServer((connection) => {
    console_log("Client connected");
    connection.on("data", async (data) => {
      console_log(`Recived Data: ${data}` )
      const receivedData = JSON.parse(data);
      if (receivedData.type === "health_check") {
        const response = "200";
        const lengthBuffer = Buffer.alloc(4);
        lengthBuffer.writeUInt32BE(response.length, 0);
        connection.write(lengthBuffer);
        connection.write(response);
      } else if (receivedData.type === "ssr") {
        const rendered = await ssr.render(receivedData.data);
        const lengthBuffer = Buffer.alloc(4);
        lengthBuffer.writeUInt32BE(rendered.length, 0);
        connection.write(lengthBuffer);
        connection.write(rendered);
      }else if (receivedData.type === "partial_ssr"){
        const rendered = await ssr.partialRender(receivedData.data);
        const lengthBuffer = Buffer.alloc(4);
        lengthBuffer.writeUInt32BE(rendered.length, 0);
        connection.write(lengthBuffer);
        connection.write(rendered);
      }
    });

    connection.on("end", () => {
      console_log("Client disconnected");
      // shutdown();
    });
    connection.on("error", (err) => {
      console.error(`Error: ${err.message}`);
    });
  });

  server.listen(socketPath, async () => {
    console_log(`Node Bride listening on ${socketPath}`);
    if (fs.existsSync(socketPath)) {
      fs.chmodSync(socketPath, "777");
    }
  });
  // Handle shutdown signal
  const shutdown = () => {
    console_log(`Shutting down node bridge...`);
    server.close(() => {
      console_log("Bridge closed");
      try {
        if (fs.existsSync(socketPath)) {
          fs.unlinkSync(socketPath);
        }
      } catch (error) {
        console.error(error)
        process.exit(1);
      }
      process.exit(0);
    });
  };
  process.on("SIGINT", shutdown);
  process.on("SIGTERM", shutdown);
} catch (error) {
  debug_log(`Something went wrong: ${String(error)}`);
  process.exit(0);
}
