"""
Direct HTTP server implementation for Remote Work Job Board
Using only Python standard library
"""
import http.server
import json
import socketserver
from http import HTTPStatus

# Set port
PORT = 5000

# Define request handler
class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Remote Work Job Board</title>
                </head>
                <body style="font-family: sans-serif; text-align: center; margin-top: 50px;">
                    <h1 style="color: #4a6ee0;">Remote Work Job Board</h1>
                    <p>The application is starting...</p>
                </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))
        
        elif self.path == '/health':
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                'status': 'ok',
                'message': 'Server is running'
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        else:
            self.send_response(HTTPStatus.NOT_FOUND)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')

def index():
    print("Starting direct HTTP server on port", PORT)
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"Server started on port {PORT}")
        httpd.serve_forever()

def health():
    return {'status': 'ok'}

if __name__ == "__main__":
    index()