"""
Basic HTTP server using Python's built-in HTTP server
"""
import http.server
import socketserver

# Define port
PORT = 5000

# Create a very basic request handler that just responds to basic requests
class SimpleHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            # Return health check
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
        else:
            # Return simple HTML for homepage
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            response = """
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Remote Work Job Board</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 0; padding: 50px; }
                        .container { max-width: 800px; margin: 0 auto; text-align: center; }
                        h1 { color: #4a6ee0; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Remote Work Job Board</h1>
                        <p>Basic server is running. The main application will load soon.</p>
                    </div>
                </body>
            </html>
            """
            
            self.wfile.write(response.encode('utf-8'))

# This is critical for proper socket cleanup on restart
socketserver.TCPServer.allow_reuse_address = True

# Create and start server
with socketserver.TCPServer(("0.0.0.0", PORT), SimpleHandler) as httpd:
    print(f"Server running at http://0.0.0.0:{PORT}")
    httpd.serve_forever()