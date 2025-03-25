from flask import Flask, jsonify

# Create the Flask app
app = Flask(__name__)

# Health check endpoint
@app.route('/')
def index():
    return jsonify({"status": "ok", "message": "Remote Work Job Board API is running"})

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)