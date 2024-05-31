const net = require("net");
const path = require("path");
const fs = require("fs");
const SSR = require("../SSR/routes")

const socketPath = path.join(__dirname, "unix_socket.sock");

// Remove the socket file if it already exists
if (fs.existsSync(socketPath)) {
  fs.unlinkSync(socketPath);
  return
}

const debug_log = (msg)=>{
  if(process.argv.length > 2){
    const args = process.argv.slice(2)
    for(let i = 0;i<args.length;i++){
      if(args[0].includes("debug=")){
        let value = args[i].slice(args[i].indexOf("=")+1)
        if(value==="True"){
          return console.log("Node Layer: ",msg)
        }
      }
    }
    return ()=>{}
  }
  return ()=>{}
}

const console_log = debug_log


const server = net.createServer((connection) => {
  console_log("Client connected");
  connection.on("data", async(data) => {
    const receivedData = JSON.parse(data)
    if(receivedData.type === "health_check"){
      const response = "200"
      const lengthBuffer = Buffer.alloc(4);
      lengthBuffer.writeUInt32BE(response.length, 0);
      connection.write(lengthBuffer);
      connection.write(response);
    }else if(receivedData.type === "ssr"){
      const response = new SSR(receivedData.data)
      const rendered = await response.render();
      const lengthBuffer = Buffer.alloc(4);
      lengthBuffer.writeUInt32BE(rendered.length, 0);
      connection.write(lengthBuffer);
      connection.write(rendered);
    }
  });

  connection.on("end", () => {
    console_log("Client disconnected");
    shutdown()
  });
  connection.on("error", (err) => {
    console.error(`Error: ${err.message}`);
  });
});




server.listen(socketPath, async() => {
  console_log(`Server listening on ${socketPath}`);
});

// Handle shutdown signal
const shutdown = () => {
  console_log("Shutting down server...");
  server.close(() => {
    console_log("Server closed");
    if (fs.existsSync(socketPath)) {
      fs.unlinkSync(socketPath);
    }
    process.exit(0);
  });
};

process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);
