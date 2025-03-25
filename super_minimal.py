from flask import Flask

# The absolute minimum Flask application possible
app = Flask(__name__)

@app.route('/')
def index():
    return 'Remote Work API: Online'

@app.route('/health')
def health():
    return '{"status":"ok"}'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)