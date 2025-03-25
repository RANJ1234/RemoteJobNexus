from flask import Flask

app = Flask(__name__, static_folder=None, template_folder=None)

@app.route('/')
def hello():
    return 'Remote Work API is starting'