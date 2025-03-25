import http.server
import socketserver

PORT = 5000

class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'Remote Work API is starting')
        return

handler = SimpleHTTPRequestHandler
httpd = socketserver.TCPServer(("0.0.0.0", PORT), handler)
print(f"Starting server at http://0.0.0.0:{PORT}")

try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("Server stopped by user")
    httpd.server_close()