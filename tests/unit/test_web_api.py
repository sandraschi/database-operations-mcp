"""Web REST API tests — logs page standard (WEBAPP_LOGS_PAGE)."""

from fastapi.testclient import TestClient

from database_operations_mcp.http_app import build_web_app


def test_root_health():
    client = TestClient(build_web_app())
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_api_health_and_capabilities():
    client = TestClient(build_web_app())
    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.json()["mcp"] == "database-operations-mcp"

    caps = client.get("/api/capabilities")
    assert caps.status_code == 200
    body = caps.json()
    assert body["status"] == "ok"
    assert "tool_surface" in body


def test_api_tools():
    client = TestClient(build_web_app())
    response = client.get("/api/tools")
    assert response.status_code == 200
    names = {tool["name"] for tool in response.json()["tools"]}
    assert "db_connection" in names


def test_logs_query_and_export():
    client = TestClient(build_web_app())
    client.post(
        "/api/tools/call",
        json={"name": "test_db_tool", "arguments": {"db_file_path": ":memory:"}},
    )
    logs = client.get("/api/logs?limit=10&kind=tool_call").json()
    assert logs["total"] >= 1
    assert "level" in logs["entries"][0]

    stats = client.get("/api/logs/stats").json()
    assert stats["max_entries"] >= 100
    assert "by_level" in stats

    export = client.get("/api/logs/export?format=json&kind=tool_call")
    assert export.status_code == 200
    assert "application/json" in export.headers.get("content-type", "")

    cleared = client.delete("/api/logs")
    assert cleared.status_code == 200
    assert client.get("/api/logs/stats").json()["total"] == 1
