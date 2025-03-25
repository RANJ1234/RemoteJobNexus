"""
Tiny HTTP server for Remote Work Job Board
"""
import http.server
import socketserver
import json
import os

# Define port
PORT = 5000

# Create custom handler
class SimpleHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health':
            # Return health check
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        elif self.path == '/' or self.path == '':
            # Return simple HTML page
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
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
                            <p>✅ Server is running</p>
                        </div>
                        <p>Welcome to the Remote Work Job Board. The application is starting up.</p>
                        <p>This is a tiny server that should start immediately.</p>
                    </div>
                </body>
            </html>
            """
            self.wfile.write(html.encode())
        else:
            # Handle 404
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'404 - Not Found')

# Create and start server
with socketserver.TCPServer(("0.0.0.0", PORT), SimpleHandler) as httpd:
    print(f"Server running at http://0.0.0.0:{PORT}")
    httpd.serve_forever()