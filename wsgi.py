from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return "Remote Work Job Board is running! The simplest version."

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

# This ensures the app is initialized when imported
# It should help with faster startup times
app.url_map