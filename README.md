# SaaSCalc

Status: 2026-10-06, local fixes under review; these changes are not published. Owner: AgentSpore maintainers. Review by: 2027-01-06.

SaaSCalc calculates revenue, customer acquisition, retention and cash runway from numbers you enter. It has a web interface and eleven calculation API routes. The API is stateless: it does not store inputs or connect to billing accounts. Ratings are fixed heuristic labels, not financial advice or verified industry benchmarks.

## Use the web interface

1. Open [the hosted calculator](https://saascalc.agentspore.com) or your local server at `http://127.0.0.1:8000`.
2. Select a calculator, enter its required numbers, then calculate.
3. Read the result and assumptions. Use the same currency for money values in one calculation; no currency conversion is performed.

Given 100 customers and ARPU 50, MRR returns 5000 and ARR 60000. Given ARPU 50, monthly churn 5% and gross margin 80%, LTV returns 800. Given cash 60000 and monthly burn 10000, runway returns 6 months. Use the comparison tab to compare two sets of dashboard inputs, with optional period labels.

The local interface rejects empty fields, nonfinite numbers, fractional customer counts and values outside the field's range. It displays field errors without treating an empty field as zero. Comparison labels appear as text, not executable HTML. A zero result remains distinct from an unavailable (`null`) result. The hosted version may still show the earlier input and numeric errors until these fixes are released.

## Run locally

From the repository root, with [uv installed](https://docs.astral.sh/uv/getting-started/installation/), run:

```bash
uv run --no-project --python 3.12 --with fastapi --with pydantic --with uvicorn python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000` for the interface, `/docs` for interactive API documentation and `/openapi.json` for the field schema. Stop the server with Ctrl+C. This command uses an isolated uv environment; no repository dependency files need changing.

Given the running local server, this request returns `{"mrr":5000.0,"arr":60000.0}`:

```bash
curl --fail-with-body --silent --show-error http://127.0.0.1:8000/calc/mrr \
  -H 'Content-Type: application/json' \
  -d '{"customers":100,"arpu":50}'
```

## API reference

All calculation routes accept JSON by POST. Field names, defaults and constraints are defined by [models.py](models.py) and exposed through `/openapi.json`; [main.py](main.py) defines the routes.

| Route | Result |
|---|---|
| `/calc/ltv` | Lifetime value from ARPU, monthly churn and gross margin |
| `/calc/cac` | Acquisition cost from spend and acquired customers |
| `/calc/mrr` | Monthly and annual recurring revenue |
| `/calc/runway` | Cash runway from available cash and monthly burn |
| `/calc/payback` | Acquisition-cost payback period |
| `/calc/churn` | Observed period churn and normalized estimates |
| `/calc/quick-ratio` | New and expansion revenue divided by lost revenue |
| `/calc/ndr` | Net dollar retention for the starting revenue cohort |
| `/calc/rule-of-40` | Revenue growth plus profit margin, in percentage points |
| `/calc/all` | Combined dashboard metrics |
| `/calc/compare` | Differences between two dashboard periods |

`GET /health` returns `{"status":"ok"}`. ARR is included in MRR and dashboard responses; there is no separate ARR route.

## Numeric contract and assumptions

SC-01. Numeric inputs must be finite. Invalid fields return HTTP 422 with a `detail` array containing `type`, `loc` and `msg`; raw input and validator context are omitted.

SC-02. Overflowing calculations return HTTP 422 with `detail: "Calculation exceeds supported numeric range"`. NDR aggregation overflow returns the same message within the field-error array. Intermediate sums are checked too: an overflowing denominator cannot silently turn a Quick Ratio into zero. No additional business-size caps are imposed. Calculations use floating-point estimates and round outputs; this is not an accounting ledger.

SC-03. Lost customers cannot exceed the starting cohort. NDR losses cannot exceed starting revenue plus expansion. Both validation and NDR calculation use the same stable signed sum, so cancellation does not create negative ending revenue.

SC-04. Monthly and annual churn are estimates under constant cohort retention: `1 - (1 - period_churn) ** (target_days / period_days)`. One month is 30 days and one year is 360 days. Observed period churn is unchanged. Zero and complete churn remain 0% and 100%. Five lost customers out of 100 over 30 days yields 5% monthly churn and 45.96% estimated annual churn. This extrapolation assumes the same retention pattern continues; it is not a forecast.

SC-05. No lost revenue makes Quick Ratio unavailable (`null`). Zero monthly burn makes runway unavailable (`null`), rather than claiming a finite number of months. Use monthly ARPU, churn and burn consistently for lifetime value and payback inputs.

## Verify local changes

Run the API tests through Python 3.12 so imports resolve from the repository root:

```bash
uv run --no-project --python 3.12 --with pytest --with fastapi --with pydantic --with httpx python -m pytest tests/test_calculations.py -q
```

The tests exercise the real application through TestClient with synthetic inputs. They cover all eleven routes, field errors, nonfinite input, overflow, cancellation, zero values and retention assumptions. They do not prove that the hosted service runs this revision. Frontend tests, when the interface-fix branch is included, run with `node --test tests/test_frontend.cjs`.
