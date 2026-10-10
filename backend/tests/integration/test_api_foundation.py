import logging

from fastapi.testclient import TestClient

from parity.api.app import app


def test_health_is_minimal() -> None:
    response = TestClient(app).get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_unknown_route_does_not_echo_query_or_log_payload(
    caplog: object,
) -> None:
    sentinel = "PRIVATE-QUOTE-918273"
    with caplog.at_level(logging.INFO):  # type: ignore[attr-defined]
        response = TestClient(app).get(f"/missing?quote={sentinel}")
    assert response.status_code == 404
    assert sentinel not in response.text
    application_logs = "\n".join(
        record.getMessage()
        for record in caplog.records  # type: ignore[attr-defined]
        if record.name.startswith("parity")
    )
    assert sentinel not in application_logs
