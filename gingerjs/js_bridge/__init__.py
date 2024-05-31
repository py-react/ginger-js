import os
import socket
import subprocess
import struct
import time
import json



    
class JSBridge:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JSBridge, cls).__new__(cls)
            cls._instance.client = None
            cls._instance.node_process = None
            cls._instance.debug = False
        return cls._instance

    def debug_log(self, *msg):
        if(self.debug):
            print("JSBridge logs: "+str(msg))

    def initialize(self,*args,**kwargs):
        self.debug = kwargs.get("debug",False)
        dir_path = os.path.dirname(os.path.abspath(__file__))
        # Define the socket path
        socket_path = os.path.join(dir_path, 'unix_socket.sock')
        # Start the Node.js server as a subprocess
        node_process_path = os.path.join(dir_path, "unix_sock.js")
        self.node_process = subprocess.Popen(['node', node_process_path,f"debug={self.debug}"])
        self.debug_log(self.node_process.pid)
        # Create a Unix socket
        self.client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            while True:
                self.debug_log("Trying to Create a bridge between app and node")
                if os.path.exists(os.path.join(dir_path, "unix_socket.sock")):
                    # Wait a bit to ensure the server has started
                    self.debug_log(f"Calling connect")
                    self.client.connect(socket_path)
                    data = self.send_and_receive(json.dumps({"type":"health_check","data":""}))
                    self.debug_log("Connected", data)
                    break
                time.sleep(1)
            
        except Exception as e:
            self.debug_log("Exception : Unable to create bridge between app and node ",str(e))
            self.client.close()
            self.client = None
            self.debug_log("Trying to terminate the node process")
            self.node_process.terminate()
            try:
                self.node_process.wait(timeout=5)  # Wait for the process to terminate
                self.node_process = None
                self.debug_log("Terminated")
            except Exception as e:
                self.debug_log("Exception: " ,e)
                while True:
                    self.debug_log("Trying to kill the node process")
                    try:
                        self.node_process.kill()  # Force kill if it doesn't terminate in time
                        self.debug_log("Killed")
                        self.node_process = None
                        break
                    except Exception as e: 
                        self.debug_log("Exception: " ,e)

        

    def get_client(self):
        self.debug_log("Getting Client")
        if self.client is None:
            raise Exception("Client not initialized. Call initialize() first.")
        return self.client

    def send_and_receive(self, message):
        try:
            self.debug_log("Sending data to node",{message})
            self.client.sendall(message.encode('utf-8'))
            # Receive the length of the message first (4 bytes, big-endian)
            length_data = self.client.recv(4)
            if len(length_data) < 4:
                self.debug_log(f"Did not receive the complete length header => {len(length_data)} expected 4")
                # raise ValueError("Did not receive the complete length header")
            self.debug_log(f"Getting Message length")
            message_length = 1024
            try:
                message_length = struct.unpack('>I', length_data)[0]
                self.debug_log(f"Message length : {message_length}")
            except Exception as e:
                if self.debug:
                    self.debug_log("Exception: " + str(e))
                else:
                    raise Exception(str(e))
            # Receive the message data
            received_data = b''
            while len(received_data) < message_length:
                data = self.client.recv(min(1024,message_length))
                if not data:
                    break
                received_data += data
                self.debug_log(f"Chunk : {data}")
            self.debug_log("Recived Data: " ,received_data.decode('utf-8'))
            return received_data.decode('utf-8')

        except Exception as e:
            self.debug_log("Exception: " + str(e))
            return None



