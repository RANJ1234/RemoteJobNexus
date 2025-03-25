"""
Ultra lightweight HTTP server for Remote Work Job Board
"""
import http.server
import json
import os
import socketserver
import threading
import time

# Port to listen on
PORT = 5000

class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Remote Work Job Board</title>
                    <meta charset="UTF-8">
                    <style>
                        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; text-align: center; }
                        h1 { color: #4a6ee0; }
                    </style>
                </head>
                <body>
                    <h1>Remote Work Job Board</h1>
                    <p>The application is starting up. Please wait...</p>
                    <p><a href="/status">Check Status</a></p>
                </body>
            </html>
            """)
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "starting",
                "message": "The application is starting. This may take a moment."
            }).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')

def start_server():
    """Start the simple HTTP server"""
    with socketserver.TCPServer(("", PORT), SimpleHTTPRequestHandler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()

def start_flask_app():
    """Start the real Flask application after a delay"""
    time.sleep(3)  # Wait a few seconds for the simple server to start
    try:
        os.system("gunicorn --bind 127.0.0.1:5001 replit_main:app")
    except Exception as e:
        print(f"Error starting Flask app: {e}")

if __name__ == "__main__":
    # Start the simple HTTP server in the main thread
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Start the Flask app in another thread
    flask_thread = threading.Thread(target=start_flask_app)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Keep the main thread running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Server shutting down...")