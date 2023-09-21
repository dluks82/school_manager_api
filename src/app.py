from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/')
def root():
    return 'Hello from School Manager!'


# port 500 is already used in macOS
app.run(host='localhost', port=5001, debug=True)
