from __future__ import annotations


def calc_ltv(arpu: float, churn_rate_pct: float, gross_margin_pct: float = 100.0) -> dict:
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
    return {"mrr": round(mrr, 2), "arr": round(mrr * 12, 2)}


def calc_runway(cash: float, burn: float) -> dict:
    if burn <= 0:
        return {"runway_months": None, "note": "No burn"}
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
        return {"quick_ratio": None, "note": "No churn or contraction"}
    qr = (new_mrr + expansion_mrr) / lost
    return {
        "quick_ratio": round(qr, 2),
        "interpretation": "healthy (>4)" if qr > 4 else "good (2-4)" if qr >= 2 else "struggling (<2)",
    }


def calc_ndr(mrr_start: float, expansion_mrr: float, contraction_mrr: float, churned_mrr: float) -> dict:
    if mrr_start <= 0:
        return {"error": "mrr_start must be > 0"}
    ending_mrr = mrr_start + expansion_mrr - contraction_mrr - churned_mrr
    ndr = (ending_mrr / mrr_start) * 100
    if ndr >= 130:
        rating, note = "exceptional", "Hypergrowth from existing customers"
    elif ndr >= 110:
        rating, note = "healthy", "Strong retention with expansion"
    elif ndr >= 100:
        rating, note = "stable", "Growth requires new logos"
    else:
        rating, note = "at_risk", "Revenue shrinking — urgent retention needed"
    return {
        "ndr_pct": round(ndr, 1), "ending_mrr": round(ending_mrr, 2),
        "net_change_mrr": round(ending_mrr - mrr_start, 2),
        "rating": rating, "note": note,
    }


def calc_rule_of_40(revenue_growth_rate_pct: float, profit_margin_pct: float) -> dict:
    score = revenue_growth_rate_pct + profit_margin_pct
    if score >= 40:
        rating, note = "healthy", "Good balance of growth and profitability"
    elif score >= 20:
        rating, note = "acceptable", "Below Rule of 40 — room for improvement"
    else:
        rating, note = "needs_improvement", "Growth not compensating for losses"
    return {
        "rule_of_40_score": round(score, 1),
        "revenue_growth_rate_pct": revenue_growth_rate_pct,
        "profit_margin_pct": profit_margin_pct,
        "rating": rating, "note": note, "passes": score >= 40,
    }


def calc_all(data: dict) -> dict:
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
        "mrr": data["mrr"], "arr": round(data["mrr"] * 12, 2),
        "ltv": ltv, "cac": cac, "ltv_cac_ratio": ltv_cac,
        "runway": runway, "payback": payback,
        "churn_rate_pct": data["churn_rate_pct"],
    }


def _delta(a: float | None, b: float | None) -> dict:
    if a is None or b is None:
        return {"value_a": a, "value_b": b, "delta": None, "pct_change": None, "trend": "n/a"}
    delta = b - a
    pct = round((delta / a) * 100, 1) if a != 0 else None
    if delta > 0:
        trend = "up"
    elif delta < 0:
        trend = "down"
    else:
        trend = "flat"
    return {
        "value_a": round(a, 2), "value_b": round(b, 2),
        "delta": round(delta, 2), "pct_change": pct, "trend": trend,
    }


def _delta_inverse(a: float | None, b: float | None) -> dict:
    """Like _delta but lower is better (e.g. churn, CAC, payback)."""
    d = _delta(a, b)
    if d["trend"] == "up":
        d["trend"] = "worse"
    elif d["trend"] == "down":
        d["trend"] = "better"
    return d


def calc_compare(data_a: dict, data_b: dict, label_a: str, label_b: str) -> dict:
    a = calc_all(data_a)
    b = calc_all(data_b)

    return {
        "labels": {"a": label_a, "b": label_b},
        "metrics": {
            "mrr": _delta(a["mrr"], b["mrr"]),
            "arr": _delta(a["arr"], b["arr"]),
            "ltv": _delta(a["ltv"].get("ltv"), b["ltv"].get("ltv")),
            "cac": _delta_inverse(a["cac"].get("cac"), b["cac"].get("cac")),
            "ltv_cac_ratio": _delta(
                a["ltv_cac_ratio"]["ratio"] if a["ltv_cac_ratio"] else None,
                b["ltv_cac_ratio"]["ratio"] if b["ltv_cac_ratio"] else None,
            ),
            "runway_months": _delta(
                a["runway"].get("runway_months"),
                b["runway"].get("runway_months"),
            ),
            "payback_months": _delta_inverse(
                a["payback"].get("payback_months"),
                b["payback"].get("payback_months"),
            ),
            "churn_rate_pct": _delta_inverse(a["churn_rate_pct"], b["churn_rate_pct"]),
        },
        "period_a_full": a,
        "period_b_full": b,
    }
