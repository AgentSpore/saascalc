from fastapi import FastAPI
from models import (
    LTVInput, CACInput, MRRInput, RunwayInput,
    PaybackInput, ChurnInput, QuickRatioInput,
    NDRInput, RuleOf40Input, FullMetricsInput,
)
from engine import (
    calc_ltv, calc_cac, calc_mrr, calc_runway,
    calc_payback, calc_churn, calc_quick_ratio,
    calc_ndr, calc_rule_of_40, calc_all,
)

app = FastAPI(
    title="SaasCalc",
    description="SaaS metrics calculator API — LTV, CAC, MRR, ARR, runway, churn, NDR, Rule of 40 and more. Stateless: just POST your numbers, get answers.",
    version="1.1.0",
)


@app.post("/calc/ltv")
def ltv(body: LTVInput):
    return calc_ltv(body.arpu, body.churn_rate_pct, body.gross_margin_pct)


@app.post("/calc/cac")
def cac(body: CACInput):
    return calc_cac(body.total_sales_marketing_spend, body.new_customers_acquired)


@app.post("/calc/mrr")
def mrr(body: MRRInput):
    return calc_mrr(body.customers, body.arpu)


@app.post("/calc/runway")
def runway(body: RunwayInput):
    return calc_runway(body.cash_on_hand, body.monthly_burn)


@app.post("/calc/payback")
def payback(body: PaybackInput):
    return calc_payback(body.cac, body.arpu, body.gross_margin_pct)


@app.post("/calc/churn")
def churn(body: ChurnInput):
    return calc_churn(body.customers_start, body.customers_lost, body.period_days)


@app.post("/calc/quick-ratio")
def quick_ratio(body: QuickRatioInput):
    return calc_quick_ratio(body.new_mrr, body.expansion_mrr, body.churned_mrr, body.contraction_mrr)


@app.post("/calc/ndr")
def ndr(body: NDRInput):
    """Net Dollar Retention — revenue retained and expanded from existing customers.
    >130% exceptional, >110% healthy, >100% stable, <100% at risk."""
    return calc_ndr(body.mrr_start, body.expansion_mrr, body.contraction_mrr, body.churned_mrr)


@app.post("/calc/rule-of-40")
def rule_of_40(body: RuleOf40Input):
    """Rule of 40: growth_rate% + profit_margin% >= 40 signals healthy SaaS.
    Use EBITDA or FCF margin; negative values mean cash burn."""
    return calc_rule_of_40(body.revenue_growth_rate_pct, body.profit_margin_pct)


@app.post("/calc/all")
def all_metrics(body: FullMetricsInput):
    return calc_all(body.model_dump())
