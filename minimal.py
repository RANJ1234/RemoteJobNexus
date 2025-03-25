from flask import Flask

# Create the absolute minimum Flask app - nothing extra
app = Flask(__name__, static_folder=None, template_folder=None)

@app.route('/')
def home():
    return 'Remote Work Server OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)