import http.server
import socketserver

PORT = 5000

class SimpleHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Basic HTML response
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Remote Work - Minimal Server</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
                    .container { max-width: 800px; margin: 0 auto; padding: 20px; }
                    h1 { color: #3498db; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Remote Work</h1>
                    <p>Welcome to the Remote Work job platform.</p>
                    <p>Server running in minimal mode. The application is being loaded in the background.</p>
                    <p>This is a lightweight server to ensure fast startup.</p>
                </div>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode('utf-8'))
        else:
            # Serve static files or return 404 for other routes
            super().do_GET()

# Create and start the server
with socketserver.TCPServer(("0.0.0.0", PORT), SimpleHandler) as httpd:
    print(f"Serving at http://0.0.0.0:{PORT}")
    httpd.serve_forever()