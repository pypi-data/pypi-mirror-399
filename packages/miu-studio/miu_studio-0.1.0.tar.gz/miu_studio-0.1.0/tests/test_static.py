"""Tests for static file serving."""

from fastapi.testclient import TestClient

from miu_studio.main import create_app


def test_root_serves_index_html() -> None:
    """Test root path serves index.html."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "miu Studio" in response.text


def test_static_js_accessible() -> None:
    """Test static JS file is accessible."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/static/app.js")
    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"]
    assert "WebSocket" in response.text


def test_index_html_has_required_elements() -> None:
    """Test index.html has required UI elements."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/")
    html = response.text

    # Check for essential elements
    assert 'id="chat"' in html
    assert 'id="input"' in html
    assert 'id="send"' in html
    assert 'id="status"' in html
    assert 'id="session-id"' in html


def test_app_js_has_websocket_handling() -> None:
    """Test app.js has WebSocket handling code."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/static/app.js")
    js = response.text

    # Check for essential functions
    assert "connectWebSocket" in js
    assert "handleMessage" in js
    assert "send()" in js or "function send" in js
    assert "createSession" in js


def test_root_has_csp_headers() -> None:
    """Test root path has Content-Security-Policy headers."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200

    csp = response.headers.get("content-security-policy", "")
    assert "default-src 'self'" in csp
    assert "script-src 'self'" in csp
    assert "connect-src 'self' ws: wss:" in csp
