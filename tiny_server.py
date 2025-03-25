import http.server
import socketserver

# Ultra-minimal HTTP server with no dependencies
class SimpleHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body><h1>Remote Work Job Board</h1><p>Maintenance Mode: Server Starting</p></body></html>')

if __name__ == '__main__':
    PORT = 5000
    Handler = SimpleHandler
    
    # Set to 0.0.0.0 to make server available externally
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"Serving at http://0.0.0.0:{PORT}")
        httpd.serve_forever()