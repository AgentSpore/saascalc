from collections.abc import Callable
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request

from engine import (
    calc_all,
    calc_cac,
    calc_churn,
    calc_compare,
    calc_ltv,
    calc_mrr,
    calc_ndr,
    calc_payback,
    calc_quick_ratio,
    calc_rule_of_40,
    calc_runway,
    validate_result,
)
from models import (
    CACInput,
    ChurnInput,
    CompareInput,
    FullMetricsInput,
    LTVInput,
    MRRInput,
    NDRInput,
    PaybackInput,
    QuickRatioInput,
    RuleOf40Input,
    RunwayInput,
)

app = FastAPI(
    title="SaasCalc",
    description="SaaS metrics calculator API — LTV, CAC, MRR, ARR, runway, churn, NDR, Rule of 40 and more. Stateless: just POST your numbers, get answers.",
    version="1.2.0",
)


@app.exception_handler(RequestValidationError)
async def validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Return serializable field errors even when invalid input contains NaN."""
    errors = [
        {key: error[key] for key in ("type", "loc", "msg")} for error in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": errors})


def calculate(calculation: Callable[..., dict], *args: object) -> dict:
    """Convert numeric range failures to a clear API validation response."""
    try:
        result = calculation(*args)
        validate_result(result)
    except (OverflowError, ZeroDivisionError) as exc:
        raise HTTPException(
            status_code=422, detail="Calculation exceeds supported numeric range"
        ) from exc
    return result


STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)
def index():
    html_path = STATIC_DIR / "index.html"
    if html_path.exists():
        return HTMLResponse(html_path.read_text())
    return HTMLResponse('<h1>SaasCalc API</h1><p>See <a href="/docs">/docs</a></p>')


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/calc/ltv")
def ltv(body: LTVInput):
    return calculate(calc_ltv, body.arpu, body.churn_rate_pct, body.gross_margin_pct)


@app.post("/calc/cac")
def cac(body: CACInput):
    return calculate(
        calc_cac, body.total_sales_marketing_spend, body.new_customers_acquired
    )


@app.post("/calc/mrr")
def mrr(body: MRRInput):
    return calculate(calc_mrr, body.customers, body.arpu)


@app.post("/calc/runway")
def runway(body: RunwayInput):
    return calculate(calc_runway, body.cash_on_hand, body.monthly_burn)


@app.post("/calc/payback")
def payback(body: PaybackInput):
    return calculate(calc_payback, body.cac, body.arpu, body.gross_margin_pct)


@app.post("/calc/churn")
def churn(body: ChurnInput):
    return calculate(
        calc_churn, body.customers_start, body.customers_lost, body.period_days
    )


@app.post("/calc/quick-ratio")
def quick_ratio(body: QuickRatioInput):
    return calculate(
        calc_quick_ratio,
        body.new_mrr,
        body.expansion_mrr,
        body.churned_mrr,
        body.contraction_mrr,
    )


@app.post("/calc/ndr")
def ndr(body: NDRInput):
    return calculate(
        calc_ndr,
        body.mrr_start,
        body.expansion_mrr,
        body.contraction_mrr,
        body.churned_mrr,
    )


@app.post("/calc/rule-of-40")
def rule_of_40(body: RuleOf40Input):
    return calculate(
        calc_rule_of_40, body.revenue_growth_rate_pct, body.profit_margin_pct
    )


@app.post("/calc/all")
def all_metrics(body: FullMetricsInput):
    return calculate(calc_all, body.model_dump())


@app.post("/calc/compare")
def compare(body: CompareInput):
    """Compare SaaS metrics between two periods side-by-side.
    Returns each metric with value_a, value_b, delta, pct_change, and trend."""
    d = body.model_dump()
    return calculate(
        calc_compare,
        d["period_a"],
        d["period_b"],
        d["period_a_label"],
        d["period_b_label"],
    )
