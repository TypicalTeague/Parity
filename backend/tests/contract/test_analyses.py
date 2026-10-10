import json
from pathlib import Path

from fastapi.testclient import TestClient

from parity.api.app import app

REPO_ROOT = Path(__file__).resolve().parents[3]
REQUEST = json.loads((REPO_ROOT / "contracts/fixtures/canonical-v1.request.json").read_text())
EXPECTED = json.loads((REPO_ROOT / "contracts/fixtures/canonical-v1.response.json").read_text())


def test_canonical_analysis_returns_complete_waterfall() -> None:
    response = TestClient(app).post("/api/v1/analyses", json=REQUEST)
    assert response.status_code == 200
    body = response.json()
    assert set(body["waterfall"]) == {
        "independence_baseline",
        "correlation_adjustment",
        "model_fair_value",
        "quote_difference",
        "fees",
        "net_expected_value",
    }
    assert body["waterfall"]["independence_baseline"]["value"] == "0.300000"
    assert body["correlation"]["status"] == "coherent"
    assert body["fallback_used"] is True
    assert body["waterfall"]["fees"]["status"] == "unavailable"
    assert body["waterfall"]["net_expected_value"]["available"] is False
    assert body == EXPECTED
    assert response.headers["cache-control"] == "no-store, private, max-age=0, must-revalidate"


def test_canonical_analysis_is_byte_stable() -> None:
    client = TestClient(app)
    responses = [client.post("/api/v1/analyses", json=REQUEST).content for _ in range(10)]
    assert len(set(responses)) == 1


def test_live_mode_fails_closed_and_offers_explicit_demo() -> None:
    live = {**REQUEST, "market_inputs": {"mode": "live"}}
    response = TestClient(app).post("/api/v1/analyses", json=live)
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "LIVE_DATA_UNAVAILABLE"
    assert response.json()["error"]["fallback"] == {
        "scenario_id": "canonical-v1",
        "requires_explicit_request": True,
    }


def test_unknown_fixture_returns_domain_error() -> None:
    unknown = {
        **REQUEST,
        "market_inputs": {"mode": "deterministic_demo", "fixture_version": "unknown-v1"},
    }
    response = TestClient(app).post("/api/v1/analyses", json=unknown)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "UNSUPPORTED_COMBO"


def test_validation_error_never_echoes_submitted_value() -> None:
    sentinel = "PRIVATE-QUOTE-918273"
    invalid = {**REQUEST, "quote": {**REQUEST["quote"], "price_per_contract": sentinel}}
    response = TestClient(app).post("/api/v1/analyses", json=invalid)
    assert response.status_code == 422
    assert sentinel not in response.text
