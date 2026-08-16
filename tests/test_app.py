import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from app import app


def test_home_page():
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    assert b"URL Shortener" in response.data


def test_invalid_short_code():
    client = app.test_client()

    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None

    mock_connection = MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

    with patch("app.redis_client") as mock_redis:
        mock_redis.get.return_value = None

        with patch("app.get_db", return_value=mock_connection):
            response = client.get("/doesnotexist")

    assert response.status_code == 404
