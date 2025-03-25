from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return "Remote Work Job Board is running! Direct server version."

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    # Run directly with Python instead of Gunicorn
    print("Starting direct Flask server on port 5000...")
    app.run(host="0.0.0.0", port=5000)