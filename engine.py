"""
Pure calculation functions — no DB needed, all stateless math.
"""
from __future__ import annotations


def calc_ltv(arpu: float, churn_rate_pct: float, gross_margin_pct: float = 100.0) -> dict:
    """
    LTV = (ARPU / monthly_churn_rate) * (gross_margin / 100)
    Uses simple avg LTV formula; adequate for early-stage SaaS.
    """
    if churn_rate_pct <= 0:
        return {"error": "churn_rate_pct must be > 0"}
    monthly_churn = churn_rate_pct / 100
    avg_customer_lifetime_months = 1 / monthly_churn
    ltv = arpu * avg_customer_lifetime_months * (gross_margin_pct / 100)
    return {
        "ltv": round(ltv, 2),
        "avg_lifetime_months": round(avg_customer_lifetime_months, 1),
        "formula": "ARPU / churn_rate * gross_margin",
    }


def calc_cac(spend: float, acquired: int) -> dict:
    if acquired <= 0:
        return {"error": "new_customers_acquired must be > 0"}
    return {
        "cac": round(spend / acquired, 2),
        "formula": "total_sales_marketing_spend / new_customers_acquired",
    }


def calc_mrr(customers: int, arpu: float) -> dict:
    mrr = customers * arpu
    return {
        "mrr": round(mrr, 2),
        "arr": round(mrr * 12, 2),
    }


def calc_runway(cash: float, burn: float) -> dict:
    if burn <= 0:
        return {"runway_months": None, "note": "No burn — profitable or pre-revenue"}
    months = cash / burn
    return {
        "runway_months": round(months, 1),
        "runway_days": round(months * 30, 0),
        "zero_date_approx": f"{int(months)} months from now",
    }


def calc_payback(cac: float, arpu: float, gross_margin_pct: float = 100.0) -> dict:
    if arpu <= 0 or gross_margin_pct <= 0:
        return {"error": "arpu and gross_margin_pct must be > 0"}
    monthly_gp = arpu * (gross_margin_pct / 100)
    payback_months = cac / monthly_gp
    return {
        "payback_months": round(payback_months, 1),
        "payback_years": round(payback_months / 12, 2),
        "rating": "excellent" if payback_months <= 12 else "good" if payback_months <= 18 else "needs_improvement",
    }


def calc_churn(customers_start: int, lost: int, period_days: int = 30) -> dict:
    if customers_start <= 0:
        return {"error": "customers_start must be > 0"}
    rate = lost / customers_start
    monthly_rate = rate * (30 / period_days)
    annual_rate = 1 - (1 - monthly_rate) ** 12
    return {
        "period_churn_pct": round(rate * 100, 2),
        "monthly_churn_pct": round(monthly_rate * 100, 2),
        "annual_churn_pct": round(annual_rate * 100, 2),
        "rating": "excellent" if monthly_rate <= 0.01 else "good" if monthly_rate <= 0.03 else "needs_improvement",
    }


def calc_quick_ratio(new_mrr: float, expansion_mrr: float, churned_mrr: float, contraction_mrr: float) -> dict:
    lost = churned_mrr + contraction_mrr
    if lost <= 0:
        return {"quick_ratio": None, "note": "No churn or contraction — best case"}
    qr = (new_mrr + expansion_mrr) / lost
    return {
        "quick_ratio": round(qr, 2),
        "interpretation": "healthy (>4)" if qr > 4 else "good (2-4)" if qr >= 2 else "struggling (<2)",
    }


def calc_all(data: dict) -> dict:
    """Compute all metrics at once from a single input payload."""
    ltv = calc_ltv(data["arpu"], data["churn_rate_pct"], data["gross_margin_pct"])
    cac = calc_cac(data["total_sales_marketing_spend"], data["new_customers_acquired"])
    mrr = calc_mrr(data.get("customers", 1), data["mrr"] / max(data.get("customers", 1), 1))
    runway = calc_runway(data["cash_on_hand"], data["monthly_burn"])
    payback = calc_payback(cac.get("cac", 0), data["arpu"], data["gross_margin_pct"])

    ltv_cac = None
    if cac.get("cac") and ltv.get("ltv"):
        ltv_cac_val = ltv["ltv"] / cac["cac"]
        ltv_cac = {
            "ratio": round(ltv_cac_val, 2),
            "rating": "excellent (>5)" if ltv_cac_val > 5 else "good (3-5)" if ltv_cac_val >= 3 else "needs_improvement (<3)",
        }

    return {
        "mrr": data["mrr"],
        "arr": round(data["mrr"] * 12, 2),
        "ltv": ltv,
        "cac": cac,
        "ltv_cac_ratio": ltv_cac,
        "runway": runway,
        "payback": payback,
        "churn_rate_pct": data["churn_rate_pct"],
    }
