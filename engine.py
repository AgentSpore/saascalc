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


def calc_ndr(mrr_start: float, expansion_mrr: float, contraction_mrr: float, churned_mrr: float) -> dict:
    """
    Net Dollar Retention = (MRR_start + expansion - contraction - churned) / MRR_start * 100
    Measures revenue retained + grown from existing customers, excluding new logos.
    >130% = exceptional (hypergrowth from expansion), >110% = healthy, >100% = stable, <100% = at risk.
    """
    if mrr_start <= 0:
        return {"error": "mrr_start must be > 0"}
    ending_mrr = mrr_start + expansion_mrr - contraction_mrr - churned_mrr
    ndr = (ending_mrr / mrr_start) * 100
    if ndr >= 130:
        rating = "exceptional"
        note = "Hypergrowth from existing customers — expansion revenue far outpaces churn"
    elif ndr >= 110:
        rating = "healthy"
        note = "Strong retention with meaningful expansion revenue"
    elif ndr >= 100:
        rating = "stable"
        note = "Existing customers cover their own churn — growth requires new logos"
    else:
        rating = "at_risk"
        note = "Revenue from existing customers is shrinking — urgent retention action needed"
    return {
        "ndr_pct": round(ndr, 1),
        "ending_mrr": round(ending_mrr, 2),
        "net_change_mrr": round(ending_mrr - mrr_start, 2),
        "rating": rating,
        "note": note,
        "formula": "(mrr_start + expansion - contraction - churned) / mrr_start * 100",
    }


def calc_rule_of_40(revenue_growth_rate_pct: float, profit_margin_pct: float) -> dict:
    """
    Rule of 40: growth_rate% + profit_margin% >= 40 indicates healthy SaaS business.
    Profit margin can be EBITDA margin or FCF margin (negative = burning cash).
    Score >= 40 = healthy, >= 20 = acceptable, < 20 = needs improvement.
    """
    score = revenue_growth_rate_pct + profit_margin_pct
    if score >= 40:
        rating = "healthy"
        note = "Business balances growth and profitability well — attractive to investors"
    elif score >= 20:
        rating = "acceptable"
        note = "Below Rule of 40 but not alarming — improving either metric will help"
    else:
        rating = "needs_improvement"
        note = "Growth is not compensating for losses — reassess burn rate or growth strategy"
    return {
        "rule_of_40_score": round(score, 1),
        "revenue_growth_rate_pct": revenue_growth_rate_pct,
        "profit_margin_pct": profit_margin_pct,
        "rating": rating,
        "note": note,
        "passes": score >= 40,
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
        "mrr": data["mrr"],
        "arr": round(data["mrr"] * 12, 2),
        "ltv": ltv,
        "cac": cac,
        "ltv_cac_ratio": ltv_cac,
        "runway": runway,
        "payback": payback,
        "churn_rate_pct": data["churn_rate_pct"],
    }
