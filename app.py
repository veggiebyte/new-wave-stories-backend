from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from auth_blueprint import authentication_blueprint
from boards_blueprint import boards_blueprint
from catalog_blueprint import catalog_blueprint

load_dotenv()

app = Flask(__name__)

CORS(
    app,
    resources={r"/*": {"origins": "http://localhost:5173"}},
    supports_credentials=True
)

app.register_blueprint(authentication_blueprint)
app.register_blueprint(boards_blueprint)
app.register_blueprint(catalog_blueprint)


@app.route("/")
def index():
    return "Hello, world!"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
