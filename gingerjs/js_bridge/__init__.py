import os
import socket
import struct
import json
class JSBridge:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JSBridge, cls).__new__(cls)
            cls._instance.socket_path = None
            cls._instance.connected = False
            cls._instance.debug = False
        return cls._instance

    def debug_log(self, *msg):
        if(self.debug):
            print(f"{os.getpid()} JSBridge logs: "+str(msg))

    def initialize(self,*args,**kwargs):
        if self.connected:
            self.debug("Client initiated")
            return
        self.debug = kwargs.get("debug",False)

        # Create a Unix socket
        try:
            # Define the socket path
            self.socket_path = "/tmp/gingerjs_unix.sock"
            # Wait a bit to ensure the server has started
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            # Wait a bit to ensure the client is connected
            self.debug_log(f"Calling connect")
            client.connect(self.socket_path)
            data = self.send_and_receive(json.dumps({"type":"health_check","data":""}))
            self.debug_log("Connected", data)
            self.connected = True
        except Exception as e:
            self.debug_log("Exception : Unable to create bridge between app and node ",str(e))

    def get_client(self):
        self.debug_log("Getting Client")
        if self.client is None:
            raise Exception("Client not initialized. Call initialize() first.")
        return self.client
    
    def send_all(self, data,client):
        """Ensure all data is sent."""
        try:
            client.connect(self.socket_path)
            length = len(data)
            try:
                length_prefix = struct.pack('!I', length)  # Pack length as 4-byte unsigned int
                message = length_prefix + data
                client.sendall(message)
            except (BrokenPipeError, ConnectionResetError, OSError) as e:
                self.debug(f"Failed to send data over socket: {e}")
                return False
        except Exception as e:
            self.debug(f"Unexpected error during sending message: {e}")

    def send_and_receive(self, message):
        try:
            received_data = b''
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                self.send_all(message.encode("utf-8"),client)
                # Receive the length of the message first (4 bytes, big-endian)
                length_data = client.recv(4)
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
                while len(received_data) < message_length:
                    data = client.recv(min(1024,message_length))
                    if not data:
                        break
                    received_data += data
                    self.debug_log(f"Chunk : {data}")
                decoded_recived_data = received_data.decode("utf-8")
                self.debug_log("Recived Data: " ,decoded_recived_data)
            return received_data.decode('utf-8')
        except FileNotFoundError:
            self.debug(f"Socket file not found: {self.socket_path}")
        except ConnectionRefusedError:
            self.debug(f"Connection refused: is the Node.js server running?")
        except Exception as e:
            self.debug(f"Unexpected error during socket communication: {e}")
            return None



