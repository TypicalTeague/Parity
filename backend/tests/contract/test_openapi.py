from fastapi.testclient import TestClient

from parity.api.app import app


def test_openapi_has_only_expected_initial_operations() -> None:
    schema = TestClient(app).get("/openapi.json").json()
    assert schema["info"]["title"] == "Parity Price Waterfall API"
    assert set(schema["paths"]) == {"/api/v1/health"}
    assert schema["paths"]["/api/v1/health"]["get"]["operationId"] == "getHealth"
