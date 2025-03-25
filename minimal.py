from flask import Flask

# Create the absolute minimum Flask app - nothing extra
app = Flask(__name__)

@app.route('/')
def home():
    return '<html><body><h1>Remote Work</h1><p>Server running in minimal mode.</p></body></html>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)