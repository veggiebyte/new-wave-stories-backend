from flask import Flask, jsonify, g, request
from flask_cors import CORS
import os
import psycopg2
import psycopg2.extras
from auth_middleware import token_required
from auth_blueprint import authentication_blueprint
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

CORS(
    app,
    resources={r"/*": {"origins": "http://localhost:5173"}},
    supports_credentials=True
)

app.register_blueprint(authentication_blueprint)


@app.route("/")
def index():
    return "Hello, world!"


def get_db_connection():
    connection = psycopg2.connect(
        host="localhost",
        database=os.getenv("POSTGRES_DATABASE"),
        user=os.getenv("POSTGRES_USERNAME"),
        password=os.getenv("POSTGRES_PASSWORD")
    )
    return connection


# -----------------------
# USERS ROUTES
# -----------------------

@app.route("/users")
@token_required
def users_index():
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("SELECT id, username FROM users;")
    users = cursor.fetchall()

    connection.close()
    return jsonify(users), 200


@app.route("/users/<user_id>")
@token_required
def users_show(user_id):
    if int(user_id) != g.user["id"]:
        return jsonify({"err": "Unauthorized"}), 403

    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute(
        "SELECT id, username FROM users WHERE id = %s;",
        (user_id,)
    )

    user = cursor.fetchone()
    connection.close()

    if user is None:
        return jsonify({"err": "User not found"}), 404

    return jsonify(user), 200


# -----------------------
# BOARDS ROUTES
# -----------------------

@app.route("/boards")
@token_required
def boards_index():
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute(
        "SELECT * FROM boards WHERE user_id = %s ORDER BY created_at DESC;",
        (g.user["id"],)
    )

    boards = cursor.fetchall()
    connection.close()

    return jsonify(boards), 200


@app.route("/boards", methods=["POST"])
@token_required
def boards_create():
    data = request.get_json() or {}

    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute(
        """
        INSERT INTO boards (user_id, title, city, vibe, song)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING *;
        """,
        (
            g.user["id"],
            data.get("title"),
            data.get("city"),
            data.get("vibe"),
            data.get("song"),
        )
    )

    

    new_board = cursor.fetchone()
    connection.commit()
    connection.close()

    return jsonify(new_board), 201

@app.route("/boards/<board_id>")
@token_required
def boards_show(board_id):
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute(
        "SELECT * FROM boards WHERE id = %s AND user_id = %s;",
        (board_id, g.user["id"])
    )

    board = cursor.fetchone()
    connection.close()

    if board is None:
        return jsonify({"err": "Board not found"}), 404

    return jsonify(board), 200

@app.route("/boards/<board_id>", methods=["PUT"])
@token_required
def boards_update(board_id):
    data = request.get_json() or {}

    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute(
        """
        UPDATE boards
        SET title = COALESCE(%s, title),
            city  = COALESCE(%s, city),
            vibe  = COALESCE(%s, vibe),
            song  = COALESCE(%s, song)
        WHERE id = %s AND user_id = %s
        RETURNING *;
        """,
        (
            data.get("title"),
            data.get("city"),
            data.get("vibe"),
            data.get("song"),
            board_id,
            g.user["id"],
        )
    )

    updated_board = cursor.fetchone()
    connection.commit()
    connection.close()

    if updated_board is None:
        return jsonify({"err": "Board not found"}), 404

    return jsonify(updated_board), 200

@app.route("/boards/<board_id>", methods=["DELETE"])
@token_required
def boards_delete(board_id):
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute(
        "DELETE FROM boards WHERE id = %s AND user_id = %s RETURNING *;",
        (board_id, g.user["id"])
    )

    deleted_board = cursor.fetchone()
    connection.commit()
    connection.close()

    if deleted_board is None:
        return jsonify({"err": "Board not found"}), 404

    return jsonify({"msg": "Board deleted"}), 200

@app.route("/catalog")
@token_required
def catalog_index():
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("SELECT * FROM catalog_items ORDER BY category, name;")
    items = cursor.fetchall()

    connection.close()
    return jsonify(items), 200

@app.route("/catalog", methods=["POST"])
@token_required
def catalog_create():
    data = request.get_json() or {}

    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute(
        """
        INSERT INTO catalog_items (name, category, image_url)
        VALUES (%s, %s, %s)
        RETURNING *;
        """,
        (data.get("name"), data.get("category"), data.get("image_url"))
    )

    new_item = cursor.fetchone()
    connection.commit()
    connection.close()

    return jsonify(new_item), 201

@app.route("/boards/<board_id>/items", methods=["POST"])
@token_required
def add_item_to_board(board_id):
    data = request.get_json() or {}

    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Ensure the board belongs to the logged-in user
    cursor.execute(
        "SELECT id FROM boards WHERE id = %s AND user_id = %s;",
        (board_id, g.user["id"])
    )

    board = cursor.fetchone()
    if board is None:
        connection.close()
        return jsonify({"err": "Board not found"}), 404

    cursor.execute(
        """
        INSERT INTO board_items (board_id, catalog_item_id)
        VALUES (%s, %s)
        RETURNING *;
        """,
        (board_id, data.get("catalog_item_id"))
    )

    new_item = cursor.fetchone()
    connection.commit()
    connection.close()

    return jsonify(new_item), 201

@app.route("/boards/<board_id>/items")
@token_required
def board_items_index(board_id):
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # confirm board belongs to user
    cursor.execute(
        "SELECT id FROM boards WHERE id = %s AND user_id = %s;",
        (board_id, g.user["id"])
    )
    board = cursor.fetchone()
    if board is None:
        connection.close()
        return jsonify({"err": "Board not found"}), 404

    cursor.execute(
        """
        SELECT bi.id AS board_item_id,
               bi.sort_index,
               ci.id AS catalog_item_id,
               ci.name,
               ci.category,
               ci.image_url
        FROM board_items bi
        JOIN catalog_items ci ON ci.id = bi.catalog_item_id
        WHERE bi.board_id = %s
        ORDER BY bi.sort_index, bi.id;
        """,
        (board_id,)
    )

    items = cursor.fetchall()
    connection.close()
    return jsonify(items), 200

@app.route("/boards/<board_id>/items/<board_item_id>", methods=["DELETE"])
@token_required
def board_item_delete(board_id, board_item_id):
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # confirm board belongs to user
    cursor.execute(
        "SELECT id FROM boards WHERE id = %s AND user_id = %s;",
        (board_id, g.user["id"])
    )
    board = cursor.fetchone()
    if board is None:
        connection.close()
        return jsonify({"err": "Board not found"}), 404

    cursor.execute(
        "DELETE FROM board_items WHERE id = %s AND board_id = %s RETURNING *;",
        (board_item_id, board_id)
    )
    deleted = cursor.fetchone()
    connection.commit()
    connection.close()

    if deleted is None:
        return jsonify({"err": "Item not found"}), 404

    return jsonify({"msg": "Item removed"}), 200


@app.route("/boards/<board_id>/items/<board_item_id>", methods=["PUT"])
@token_required
def board_item_update(board_id, board_item_id):
    data = request.get_json() or {}

    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # confirm board belongs to user
    cursor.execute(
        "SELECT id FROM boards WHERE id = %s AND user_id = %s;",
        (board_id, g.user["id"])
    )
    board = cursor.fetchone()
    if board is None:
        connection.close()
        return jsonify({"err": "Board not found"}), 404

    cursor.execute(
        """
        UPDATE board_items
        SET sort_index = COALESCE(%s, sort_index)
        WHERE id = %s AND board_id = %s
        RETURNING *;
        """,
        (data.get("sort_index"), board_item_id, board_id)
    )

    updated = cursor.fetchone()
    connection.commit()
    connection.close()

    if updated is None:
        return jsonify({"err": "Item not found"}), 404

    return jsonify(updated), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
