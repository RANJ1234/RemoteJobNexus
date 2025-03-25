from flask import Flask

# Create a minimal test app
app = Flask(__name__)

@app.route('/')
def hello():
    return """
    <html>
    <head>
        <title>Server Test</title>
    </head>
    <body>
        <h1>Server is running!</h1>
        <p>The minimal Flask app is working correctly.</p>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)