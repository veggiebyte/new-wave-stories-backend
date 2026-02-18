from flask import Blueprint, jsonify, request, g
import psycopg2.extras

from auth_middleware import token_required
from db_helpers import get_db_connection

import os
from anthropic import Anthropic

boards_blueprint = Blueprint("boards_blueprint", __name__)

# Rate limiting for story generation
story_counts = {}


# -----------------------
# BOARDS
# -----------------------

@boards_blueprint.route("/boards/<board_id>/generate-story", methods=["POST"])
@token_required
def generate_story(board_id):
    user_id = g.user["id"]
    
    # Limit: 5 stories per user
    if story_counts.get(user_id, 0) >= 5:
        return jsonify({"err": "Story generation limit reached"}), 429
    
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    cursor.execute(
        "SELECT * FROM boards WHERE id = %s AND user_id = %s;",
        (board_id, g.user["id"])
    )
    board = cursor.fetchone()
    
    if not board:
        connection.close()
        return jsonify({"err": "Board not found"}), 404
    
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    prompt = f"Write a short, atmospheric 2-3 sentence scene set in a {board['city']} nightclub in the early 1980s new wave era. The vibe is {board['vibe']}. The song playing is {board['song']}. Focus on the mood, the crowd, and the energy of the night."
    
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}]
    )
    
    story = message.content[0].text
    
    cursor.execute(
        "UPDATE boards SET story = %s WHERE id = %s RETURNING *;",
        (story, board_id)
    )
    updated = cursor.fetchone()
    connection.commit()
    connection.close()
    
    story_counts[user_id] = story_counts.get(user_id, 0) + 1
    
    return jsonify(updated), 200

@boards_blueprint.route("/boards")
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


@boards_blueprint.route("/boards", methods=["POST"])
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


@boards_blueprint.route("/boards/<board_id>")
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


@boards_blueprint.route("/boards/<board_id>", methods=["PUT"])
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
            song  = COALESCE(%s, song),
            story = COALESCE(%s, story)
        WHERE id = %s AND user_id = %s
        RETURNING *;
        """,
        (
            data.get("title"),
            data.get("city"),
            data.get("vibe"),
            data.get("song"),
            data.get("story"),
            board_id,
            g.user["id"],
        )
    )

    updated = cursor.fetchone()
    connection.commit()
    connection.close()

    if updated is None:
        return jsonify({"err": "Board not found"}), 404

    return jsonify(updated), 200


@boards_blueprint.route("/boards/<board_id>", methods=["DELETE"])
@token_required
def boards_delete(board_id):
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute(
        "DELETE FROM boards WHERE id = %s AND user_id = %s RETURNING *;",
        (board_id, g.user["id"])
    )
    deleted = cursor.fetchone()
    connection.commit()
    connection.close()

    if deleted is None:
        return jsonify({"err": "Board not found"}), 404

    return jsonify({"msg": "Board deleted"}), 200


# -----------------------
# BOARD ITEMS
# -----------------------

@boards_blueprint.route("/boards/<board_id>/items", methods=["POST"])
@token_required
def add_item_to_board(board_id):
    data = request.get_json() or {}

    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

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


@boards_blueprint.route("/boards/<board_id>/items")
@token_required
def board_items_index(board_id):
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

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


@boards_blueprint.route("/boards/<board_id>/items/<board_item_id>", methods=["PUT"])
@token_required
def board_item_update(board_id, board_item_id):
    data = request.get_json() or {}

    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

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


@boards_blueprint.route("/boards/<board_id>/items/<board_item_id>", methods=["DELETE"])
@token_required
def board_item_delete(board_id, board_item_id):
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

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