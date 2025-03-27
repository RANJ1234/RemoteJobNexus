import os
import sys
import cgi

# Add the application directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Simple WSGI application function
def application(environ, start_response):
    status = '200 OK'
    output = b'Remote Work Server OK - Successfully Deployed!'
    
    response_headers = [
        ('Content-type', 'text/html'),
        ('Content-Length', str(len(output)))
    ]
    
    start_response(status, response_headers)
    return [output]

# The following is the main entry point for PythonHandler
def handler(req):
    return application

# This is for older cPanel configurations
from wsgiref.simple_server import make_server

if __name__ == '__main__':
    httpd = make_server('localhost', 8000, application)
    httpd.serve_forever() 