from flask import Flask, jsonify, redirect
import os
from dotenv import load_dotenv

# loading .env file
load_dotenv()

# .env variables
DEBUG = os.getenv("DEBUG", False)

app = Flask(__name__)


@app.route("/", methods=["GET"])
def main_path():
    return redirect("/hello", code=302)

@app.route("/hello", methods=["GET"])
def hello():
    return jsonify(message="Hello world")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=DEBUG)