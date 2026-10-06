import pytest
from fastapi.testclient import TestClient

from main import app

FULL = {
    "arpu": 50,
    "churn_rate_pct": 5,
    "gross_margin_pct": 80,
    "total_sales_marketing_spend": 1000,
    "new_customers_acquired": 10,
    "cash_on_hand": 10000,
    "monthly_burn": 1000,
    "mrr": 5000,
}
CASES = [
    ("ltv", {"arpu": 50, "churn_rate_pct": 5}, "ltv", 1000),
    (
        "cac",
        {"total_sales_marketing_spend": 1000, "new_customers_acquired": 10},
        "cac",
        100,
    ),
    ("mrr", {"customers": 100, "arpu": 50}, "mrr", 5000),
    ("runway", {"cash_on_hand": 10000, "monthly_burn": 1000}, "runway_months", 10),
    ("payback", {"cac": 100, "arpu": 50}, "payback_months", 2),
    ("churn", {"customers_start": 100, "customers_lost": 5}, "period_churn_pct", 5),
    (
        "quick-ratio",
        {
            "new_mrr": 500,
            "expansion_mrr": 100,
            "churned_mrr": 50,
            "contraction_mrr": 50,
        },
        "quick_ratio",
        6,
    ),
    (
        "ndr",
        {
            "mrr_start": 1000,
            "expansion_mrr": 200,
            "contraction_mrr": 50,
            "churned_mrr": 50,
        },
        "ndr_pct",
        110,
    ),
    (
        "rule-of-40",
        {"revenue_growth_rate_pct": 30, "profit_margin_pct": 10},
        "rule_of_40_score",
        40,
    ),
    ("all", FULL, "arr", 60000),
    (
        "compare",
        {"period_a": FULL, "period_b": FULL},
        "labels",
        {"a": "Period A", "b": "Period B"},
    ),
]


@pytest.fixture
def client():
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


@pytest.mark.parametrize("endpoint,payload,key,expected", CASES)
def test_happy_path(client, endpoint, payload, key, expected):
    response = client.post(f"/calc/{endpoint}", json=payload)
    assert response.status_code == 200
    assert response.json()[key] == expected


@pytest.mark.parametrize(
    "endpoint,payload,field",
    [
        (endpoint, payload, field)
        for endpoint, payload, _, _ in CASES
        if endpoint != "compare"
        for field in payload
    ]
    + [("compare", {"period_a": FULL, "period_b": FULL}, field) for field in FULL],
)
@pytest.mark.parametrize("value", ["Infinity", "-Infinity", "NaN"])
def test_nonfinite_input(client, endpoint, payload, field, value):
    body = dict(payload)
    if endpoint == "compare":
        body["period_a"] = {**FULL, field: value}
    else:
        body[field] = value
    response = client.post(f"/calc/{endpoint}", json=body)
    assert response.status_code == 422
    assert response.json()["detail"]


@pytest.mark.parametrize("constant", ["Infinity", "-Infinity", "NaN"])
def test_nonstandard_json_constants(client, constant):
    response = client.post(
        "/calc/mrr",
        content='{"customers":1,"arpu":' + constant + "}",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422
    assert response.json()["detail"]


@pytest.mark.parametrize(
    "endpoint,payload",
    [
        ("mrr", {"customers": 10, "arpu": 1e308}),
        ("ltv", {"arpu": 50, "churn_rate_pct": 1e-308}),
        ("ltv", {"arpu": 50, "churn_rate_pct": 5e-324}),
        ("runway", {"cash_on_hand": 1e308, "monthly_burn": 1e-308}),
        ("payback", {"cac": 100, "arpu": 5e-324, "gross_margin_pct": 1}),
        (
            "quick-ratio",
            {
                "new_mrr": 1e308,
                "expansion_mrr": 1e308,
                "churned_mrr": 1,
                "contraction_mrr": 0,
            },
        ),
        (
            "ndr",
            {
                "mrr_start": 1e-308,
                "expansion_mrr": 1e308,
                "contraction_mrr": 0,
                "churned_mrr": 0,
            },
        ),
        ("rule-of-40", {"revenue_growth_rate_pct": 1e308, "profit_margin_pct": 1e308}),
        ("all", {**FULL, "mrr": 1e308}),
        ("compare", {"period_a": {**FULL, "mrr": 1e-308}, "period_b": FULL}),
    ],
)
def test_unrepresentable_result(client, endpoint, payload):
    response = client.post(f"/calc/{endpoint}", json=payload)
    assert response.status_code == 422
    assert "numeric range" in response.json()["detail"]


def test_lost_customers_exceed_start(client):
    response = client.post(
        "/calc/churn",
        json={"customers_start": 100, "customers_lost": 101, "period_days": 30},
    )
    assert response.status_code == 422
    assert "customers_lost" in str(response.json())


@pytest.mark.parametrize(
    "endpoint,payload,key,expected",
    [
        ("mrr", {"customers": 0, "arpu": 50}, "mrr", 0),
        ("runway", {"cash_on_hand": 1000, "monthly_burn": 0}, "runway_months", None),
        ("runway", {"cash_on_hand": 0, "monthly_burn": 100}, "runway_months", 0),
        ("payback", {"cac": 0, "arpu": 50}, "payback_months", 0),
        (
            "quick-ratio",
            {
                "new_mrr": 100,
                "expansion_mrr": 0,
                "churned_mrr": 0,
                "contraction_mrr": 0,
            },
            "quick_ratio",
            None,
        ),
        (
            "churn",
            {"customers_start": 100, "customers_lost": 100},
            "period_churn_pct",
            100,
        ),
    ],
)
def test_zero_and_boundary_semantics(client, endpoint, payload, key, expected):
    response = client.post(f"/calc/{endpoint}", json=payload)
    assert response.status_code == 200
    assert response.json()[key] == expected


@pytest.mark.parametrize(
    "lost,days,monthly,annual",
    [
        (90, 1, 100, 100),
        (50, 60, 29.29, 98.44),
        (5, 30, 5, 45.96),
        (0, 1, 0, 0),
        (100, 60, 100, 100),
    ],
)
def test_compound_churn_estimates(client, lost, days, monthly, annual):
    response = client.post(
        "/calc/churn",
        json={"customers_start": 100, "customers_lost": lost, "period_days": days},
    )
    assert response.status_code == 200
    result = response.json()
    assert result["period_churn_pct"] == lost
    assert result["monthly_churn_pct"] == monthly
    assert result["annual_churn_pct"] == annual


def test_negative_ending_mrr_rejected(client):
    response = client.post(
        "/calc/ndr",
        json={
            "mrr_start": 100,
            "expansion_mrr": 0,
            "contraction_mrr": 150,
            "churned_mrr": 0,
        },
    )
    assert response.status_code == 422


def test_expansion_can_cover_contraction(client):
    response = client.post(
        "/calc/ndr",
        json={
            "mrr_start": 100,
            "expansion_mrr": 50,
            "contraction_mrr": 120,
            "churned_mrr": 0,
        },
    )
    assert response.status_code == 200
    assert response.json()["ending_mrr"] == 30


@pytest.mark.parametrize(
    "case",
    [
        (1e16, 1, 1e16, 1, 0),
        (1e16, 1, 1e16, 0, 1),
        (1e16, 2, 1e16, 1, 1),
        (1e16, 1, 1e16, 2, None),
        (1, 1e16, 1e16, 1, 0),
        (1, 1e16, 1e16, 2, None),
        (1e308, 1e308, 0, 0, None),
        (1, 0, 1e308, 1e308, None),
    ],
)
def test_ndr_stable_aggregation(client, case):
    start, expansion, contraction, churn, ending = case
    response = client.post(
        "/calc/ndr",
        json={
            "mrr_start": start,
            "expansion_mrr": expansion,
            "contraction_mrr": contraction,
            "churned_mrr": churn,
        },
    )
    if ending is None:
        assert response.status_code == 422
        assert response.json()["detail"]
    else:
        assert response.status_code == 200
        assert response.json()["ending_mrr"] == ending


@pytest.mark.parametrize("growth,loss", [(1e308, 1), (1, 1e308), (1e308, 1e308)])
def test_quick_ratio_intermediate_overflow(client, growth, loss):
    response = client.post(
        "/calc/quick-ratio",
        json={
            "new_mrr": growth,
            "expansion_mrr": growth,
            "churned_mrr": loss,
            "contraction_mrr": loss,
        },
    )
    assert response.status_code == 422
    assert "numeric range" in response.json()["detail"]


def test_quick_ratio_denominator_overflow(client):
    response = client.post(
        "/calc/quick-ratio",
        json={
            "new_mrr": 1e308,
            "expansion_mrr": 0,
            "churned_mrr": 1e308,
            "contraction_mrr": 1e308,
        },
    )
    assert response.status_code == 422
    assert "numeric range" in response.json()["detail"]
