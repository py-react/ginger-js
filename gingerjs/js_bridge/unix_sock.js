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
    return console.log(`${process.pid} Node Bridge: ${msg}`);
  }
  return ;
};

debug_log("Running in debug mode, This setting is Not Recomeneded for production use")
const cwd = getArgValue("cwd",path.join("./"));
const ssr = new SSR(cwd);
try {
  const console_log = debug_log;

  // const args = process.argv.slice(2);
  const socketPath = getArgValue("sock_path",path.join(__dirname,"_gingerjs", `unix.sock`));
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
    debug_log("Client connected");

    let buffer = Buffer.alloc(0);
    let expectedLength = null;

    connection.on("data", async (data) => {
        buffer = Buffer.concat([buffer, data]);

        while (true) {
            if (expectedLength === null) {
                if (buffer.length >= 4) {
                    expectedLength = buffer.readUInt32BE(0);
                    buffer = buffer.slice(4);
                } else {
                    break;
                }
            }

            if (expectedLength !== null && buffer.length >= expectedLength) {
                const message = buffer.slice(0, expectedLength).toString();
                debug_log(`Received Data: ${message}`);

                // Parse received data as JSON
                let receivedData;
                try {
                    receivedData = JSON.parse(message);
                } catch (err) {
                    console.error(`Error parsing JSON: ${err}`);
                    break;
                }

                // Handle different types of data
                if (receivedData.type === "health_check") {
                    const response = "200";
                    const lengthBuffer = Buffer.alloc(4);
                    lengthBuffer.writeUInt32BE(response.length, 0);
                    connection.write(lengthBuffer);
                    connection.write(response);
                } else if (receivedData.type === "ssr" || receivedData.type === "partial_ssr") {
                    let rendered;
                    if (receivedData.type === "ssr") {
                        rendered = await ssr.render(receivedData.data);
                    } else {
                        rendered = await ssr.partialRender(receivedData.data);
                    }
                    const lengthBuffer = Buffer.alloc(4);
                    lengthBuffer.writeUInt32BE(rendered.length, 0);
                    connection.write(lengthBuffer);
                    connection.write(rendered);
                }

                // Reset for next message
                buffer = buffer.slice(expectedLength);
                expectedLength = null;
            } else {
                break;
            }
        }
    });

    connection.on("end", () => {
        debug_log("Client disconnected");
        // Perform cleanup if needed
        
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
