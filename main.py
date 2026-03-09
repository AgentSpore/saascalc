from fastapi import FastAPI
from models import (
    LTVInput, CACInput, MRRInput, RunwayInput,
    PaybackInput, ChurnInput, QuickRatioInput, FullMetricsInput,
)
from engine import (
    calc_ltv, calc_cac, calc_mrr, calc_runway,
    calc_payback, calc_churn, calc_quick_ratio, calc_all,
)

app = FastAPI(
    title="SaasCalc",
    description="SaaS metrics calculator API — LTV, CAC, MRR, ARR, runway, churn, payback period and more. Stateless: just POST your numbers, get answers.",
    version="1.0.0",
)


@app.post("/calc/ltv")
def ltv(body: LTVInput):
    """Customer Lifetime Value = ARPU / churn_rate * gross_margin."""
    return calc_ltv(body.arpu, body.churn_rate_pct, body.gross_margin_pct)


@app.post("/calc/cac")
def cac(body: CACInput):
    """Customer Acquisition Cost = total_spend / new_customers."""
    return calc_cac(body.total_sales_marketing_spend, body.new_customers_acquired)


@app.post("/calc/mrr")
def mrr(body: MRRInput):
    """MRR and ARR from customer count and ARPU."""
    return calc_mrr(body.customers, body.arpu)


@app.post("/calc/runway")
def runway(body: RunwayInput):
    """Runway in months and days from cash balance and monthly burn."""
    return calc_runway(body.cash_on_hand, body.monthly_burn)


@app.post("/calc/payback")
def payback(body: PaybackInput):
    """CAC payback period in months. Rated: excellent <12mo, good <18mo."""
    return calc_payback(body.cac, body.arpu, body.gross_margin_pct)


@app.post("/calc/churn")
def churn(body: ChurnInput):
    """Monthly and annual churn rate from period data. Rated: excellent <1%/mo."""
    return calc_churn(body.customers_start, body.customers_lost, body.period_days)


@app.post("/calc/quick-ratio")
def quick_ratio(body: QuickRatioInput):
    """Growth efficiency: (new + expansion MRR) / (churned + contraction MRR). >4 = healthy."""
    return calc_quick_ratio(body.new_mrr, body.expansion_mrr, body.churned_mrr, body.contraction_mrr)


@app.post("/calc/all")
def all_metrics(body: FullMetricsInput):
    """Compute all key SaaS metrics at once. Returns LTV, CAC, LTV/CAC, runway, payback, ARR."""
    return calc_all(body.model_dump())
