#!/usr/bin/python
import cgi
import cgitb
cgitb.enable()

print("Content-Type: text/html\n\n")
print("""
<!DOCTYPE html>
<html>
<head>
    <title>Remote Job Nexus</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #0066cc; }
        .container { max-width: 800px; margin: 0 auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Remote Job Nexus</h1>
        <p>Python CGI is working correctly!</p>
        <p>This is a fallback page to ensure that Python execution is working on your server.</p>
        <p>To see the full WSGI application, please check the passenger_wsgi.py configuration.</p>
    </div>
</body>
</html>
""") 