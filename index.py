#!/usr/bin/python
print("Content-Type: text/html\n\n")
print("""
<!DOCTYPE html>
<html>
<head>
    <title>Remote Job Nexus</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        h1 { color: #2c3e50; }
        .container { max-width: 800px; margin: 0 auto; }
        .success { color: #27ae60; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Remote Job Nexus</h1>
        <p class="success">✓ Python CGI application successfully deployed!</p>
        <p>This is a simple Python script running as a CGI application.</p>
        <p>The web server is now correctly configured to run Python scripts.</p>
    </div>
</body>
</html>
""") 