"""
Socket-level server for Remote Work Job Board
"""
import socket
import signal
import sys
import threading
import time

def create_server_socket():
    """Create a server socket on port 5000"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 5000))
    server_socket.listen(5)
    return server_socket

def handle_connection(client_socket):
    """Handle a client connection"""
    try:
        # Receive the HTTP request
        request = client_socket.recv(1024).decode('utf-8')
        
        # Parse the request to get the path
        request_lines = request.split('\n')
        if not request_lines:
            return
            
        # Get the HTTP method and path
        first_line = request_lines[0].strip().split()
        if len(first_line) < 2:
            return
            
        path = first_line[1]
        
        # Generate the appropriate response
        if path == '/health':
            # Health check endpoint
            response = "HTTP/1.1 200 OK\r\n"
            response += "Content-Type: application/json\r\n\r\n"
            response += '{"status":"ok"}'
        else:
            # Default homepage
            response = "HTTP/1.1 200 OK\r\n"
            response += "Content-Type: text/html\r\n\r\n"
            response += """
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Remote Work Job Board</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 0; padding: 50px; background-color: #f8f9fa; }
                        .container { max-width: 800px; margin: 0 auto; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                        h1 { color: #4a6ee0; text-align: center; }
                        p { line-height: 1.6; color: #333; }
                        .status { text-align: center; margin: 20px 0; padding: 10px; background: #e8f5e9; border-radius: 5px; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Remote Work Job Board</h1>
                        <div class="status">
                            <p>✅ Socket Server is running</p>
                        </div>
                        <p>Welcome to the Remote Work Job Board. This is a super-minimal socket server.</p>
                    </div>
                </body>
            </html>
            """
        
        # Send the response
        client_socket.sendall(response.encode('utf-8'))
    except Exception as e:
        print(f"Error handling connection: {e}")
    finally:
        # Close the connection
        client_socket.close()

def accept_connections(server_socket):
    """Accept and handle incoming connections"""
    while True:
        try:
            # Accept incoming connection
            client_socket, _ = server_socket.accept()
            # Handle the connection in a new thread
            client_thread = threading.Thread(target=handle_connection, args=(client_socket,))
            client_thread.daemon = True
            client_thread.start()
        except Exception as e:
            print(f"Error accepting connection: {e}")
            break

def signal_handler(sig, frame):
    """Handle termination signals"""
    print("Server shutting down...")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Create and start the server
if __name__ == "__main__":
    server_socket = create_server_socket()
    print(f"Socket server running on http://0.0.0.0:5000")
    
    # Start accepting connections
    accept_connections(server_socket)