import os
import secrets
from datetime import datetime, timezone

import pymysql
import redis
from flask import Flask, redirect, render_template_string, request, url_for


app = Flask(__name__)


# MySQL connection
def get_db():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "urluser"),
        password=os.getenv("MYSQL_PASSWORD", "urlpassword2026"),
        database=os.getenv("MYSQL_DATABASE", "urlshortener"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )


# Redis connection
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True,
)


def init_db():
    connection = get_db()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS urls (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    original_url TEXT NOT NULL,
                    short_code VARCHAR(20) NOT NULL UNIQUE,
                    created_at DATETIME NOT NULL,
                    click_count INT NOT NULL DEFAULT 0
                )
                """
            )

        connection.commit()

    finally:
        connection.close()


def generate_short_code(length=6):
    characters = (
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789"
    )

    while True:
        short_code = "".join(
            secrets.choice(characters) for _ in range(length)
        )

        connection = get_db()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id FROM urls WHERE short_code = %s",
                    (short_code,),
                )

                existing = cursor.fetchone()

        finally:
            connection.close()

        if existing is None:
            return short_code


@app.route("/", methods=["GET"])
def index():
    return render_template_string(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>URL Shortener</title>
        </head>
        <body>
            <h1>URL Shortener</h1>

            <form method="POST" action="{{ url_for('shorten_url') }}">
                <input
                    type="url"
                    name="url"
                    placeholder="Enter a long URL"
                    required
                    size="60"
                >

                <button type="submit">
                    Shorten URL
                </button>
            </form>
        </body>
        </html>
        """
    )


@app.route("/shorten", methods=["POST"])
def shorten_url():
    original_url = request.form.get("url", "").strip()

    if not original_url:
        return "URL is required", 400

    short_code = generate_short_code()

    connection = get_db()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO urls
                (original_url, short_code, created_at, click_count)
                VALUES (%s, %s, %s, 0)
                """,
                (
                    original_url,
                    short_code,
                    datetime.now(timezone.utc).replace(tzinfo=None),
                ),
            )

        connection.commit()

    finally:
        connection.close()

    # Store the URL in Redis for fast future lookups
    redis_client.setex(
        f"url:{short_code}",
        3600,
        original_url,
    )

    short_url = url_for(
        "redirect_url",
        short_code=short_code,
        _external=True,
    )

    return render_template_string(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>URL Shortened</title>
        </head>
        <body>
            <h1>URL Shortened Successfully</h1>

            <p>
                <strong>Original URL:</strong>
                {{ original_url }}
            </p>

            <p>
                <strong>Short URL:</strong>
                <a href="{{ short_url }}">{{ short_url }}</a>
            </p>

            <p>
                <a href="{{ url_for('index') }}">
                    Shorten another URL
                </a>
            </p>
        </body>
        </html>
        """,
        original_url=original_url,
        short_url=short_url,
    )


@app.route("/<short_code>", methods=["GET"])
def redirect_url(short_code):
    # First check Redis
    original_url = redis_client.get(f"url:{short_code}")

    if original_url:
        # URL found in Redis cache
        connection = get_db()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE urls
                    SET click_count = click_count + 1
                    WHERE short_code = %s
                    """,
                    (short_code,),
                )

            connection.commit()

        finally:
            connection.close()

        return redirect(original_url)

    # Redis cache miss - query MySQL
    connection = get_db()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM urls WHERE short_code = %s",
                (short_code,),
            )

            url_record = cursor.fetchone()

            if url_record is None:
                return "Short URL not found", 404

            cursor.execute(
                """
                UPDATE urls
                SET click_count = click_count + 1
                WHERE short_code = %s
                """,
                (short_code,),
            )

        connection.commit()

        original_url = url_record["original_url"]

    finally:
        connection.close()

    # Store the URL in Redis for one hour
    redis_client.setex(
        f"url:{short_code}",
        3600,
        original_url,
    )

    return redirect(original_url)


@app.route("/stats/<short_code>", methods=["GET"])
def statistics(short_code):
    connection = get_db()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM urls WHERE short_code = %s",
                (short_code,),
            )

            url_record = cursor.fetchone()

    finally:
        connection.close()

    if url_record is None:
        return "Short URL not found", 404

    return render_template_string(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>URL Statistics</title>
        </head>
        <body>
            <h1>URL Statistics</h1>

            <p>
                <strong>Original URL:</strong>
                {{ url_record["original_url"] }}
            </p>

            <p>
                <strong>Short URL:</strong>
                {{ url_record["short_code"] }}
            </p>

            <p>
                <strong>Created:</strong>
                {{ url_record["created_at"] }}
            </p>

            <p>
                <strong>Clicks:</strong>
                {{ url_record["click_count"] }}
            </p>
        </body>
        </html>
        """,
        url_record=url_record,
    )


if __name__ == "__main__":
    init_db()

    app.run(
        host="0.0.0.0",
        port=int(os.getenv("APP_PORT", "5000")),
        debug=False,
    )
