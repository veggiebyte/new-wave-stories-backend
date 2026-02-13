from flask import Blueprint, jsonify, request
import psycopg2.extras

from auth_middleware import token_required
from db_helpers import get_db_connection

catalog_blueprint = Blueprint("catalog_blueprint", __name__)


@catalog_blueprint.route("/catalog")
@token_required
def catalog_index():
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("SELECT * FROM catalog_items ORDER BY category, name;")
    items = cursor.fetchall()

    connection.close()
    return jsonify(items), 200


@catalog_blueprint.route("/catalog", methods=["POST"])
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
