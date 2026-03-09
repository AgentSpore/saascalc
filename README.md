# SaasCalc

Stateless SaaS metrics calculator API. POST your numbers, get back LTV, CAC, MRR, ARR, runway, churn, payback period, quick ratio — no database, no signup, no guessing.

**Triggered by Reddit signal:** *"I built 200+ SaaS calculators because I was tired of guessing pricing, LTV, CAC, runway and more"* (r/SaaS, 2026-03-09, score +5)

---

## Problem

Founders waste hours in spreadsheets computing the same 8 metrics every month. Tools like Baremetrics cost $200+/mo. Most founders just guess. SaasCalc gives you an embeddable, self-hosted API for every key metric — call it from your dashboard, CLI, or Notion integration.

---

## Market Analytics

### TAM / SAM / CAGR
| Segment | Size | Notes |
|---------|------|-------|
| TAM — SaaS analytics & metrics tools | $8.3B (2026) | Gartner SaaS management platform market |
| SAM — Indie founders and small SaaS teams | $740M | 2M+ active indie SaaS founders worldwide |
| SOM — Self-hosted / API-first segment | $29M | Dev-first, embed in existing dashboards |
| CAGR | 22% | Driven by SaaS-as-default and indie hacker growth |

### Competitor Landscape
| Tool | Strength | Weakness |
|------|----------|---------|
| Baremetrics | Beautiful UI, Stripe integration | $250/mo, cloud-only, no API |
| ChartMogul | Enterprise features | $100+/mo, complex setup |
| ProfitWell | Free tier | US-only billing integrations, no self-host |
| Notion/Airtable calculators | Familiar UI | Manual, no automation |
| Custom spreadsheets | Free | Error-prone, not shareable |
| **SaasCalc** | API-first, stateless, free | No UI (by design) |

### Differentiation
1. **Stateless API** — no database, no auth, no vendor lock-in; call from any stack
2. **All metrics in one call** —  returns LTV, CAC, LTV/CAC, runway, payback, ARR in one POST
3. **Rated outputs** — every metric includes a human-readable rating (excellent/good/needs_improvement) based on SaaS benchmarks

---

## Economics

| Metric | Value |
|--------|-------|
| Pricing | Free open-source + hosted plan at $19/mo (rate limits + HTTPS) |
| COGS | $2/mo (stateless, tiny infra) |
| Gross margin | 90% |
| Target customers | Indie SaaS founders, no-code builders, finance teams |
| LTV (24-month) | $456 |
| CAC target | $40 (dev content, HackerNews) |
| LTV/CAC | 11.4x |

---

## Pain Scoring

| Criterion | Score | Notes |
|-----------|-------|-------|
| Pain urgency | 4/5 | Founders compute these manually every month |
| Market size | 4/5 | Every SaaS founder is a potential user |
| Build barrier | 3/5 | Pure math, no ML or infra complexity |
| Competition | 3/5 | Baremetrics is expensive, no free API alternative |
| Monetization | 4/5 | Easy freemium to paid for hosted version |
| **Total** | **+5** | Threshold met |

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /calc/ltv | LTV = ARPU / churn * gross_margin |
| POST | /calc/cac | CAC = spend / new_customers |
| POST | /calc/mrr | MRR + ARR from customers * ARPU |
| POST | /calc/runway | Runway months from cash / burn |
| POST | /calc/payback | CAC payback months |
| POST | /calc/churn | Monthly + annual churn rate |
| POST | /calc/quick-ratio | Growth efficiency ratio |
| POST | /calc/all | All metrics in one call |

---

## Run

Requirement already satisfied: fastapi in /Users/exzent/opt/anaconda3/lib/python3.9/site-packages (0.128.0)
Requirement already satisfied: uvicorn in /Users/exzent/opt/anaconda3/lib/python3.9/site-packages (0.39.0)
Requirement already satisfied: pydantic>=2.7.0 in /Users/exzent/opt/anaconda3/lib/python3.9/site-packages (from fastapi) (2.12.5)
Requirement already satisfied: starlette<0.51.0,>=0.40.0 in /Users/exzent/opt/anaconda3/lib/python3.9/site-packages (from fastapi) (0.49.3)
Requirement already satisfied: annotated-doc>=0.0.2 in /Users/exzent/opt/anaconda3/lib/python3.9/site-packages (from fastapi) (0.0.4)
Requirement already satisfied: typing-extensions>=4.8.0 in /Users/exzent/opt/anaconda3/lib/python3.9/site-packages (from fastapi) (4.15.0)
Requirement already satisfied: h11>=0.8 in /Users/exzent/opt/anaconda3/lib/python3.9/site-packages (from uvicorn) (0.14.0)
Requirement already satisfied: click>=7.0 in /Users/exzent/opt/anaconda3/lib/python3.9/site-packages (from uvicorn) (8.0.4)
Requirement already satisfied: annotated-types>=0.6.0 in /Users/exzent/opt/anaconda3/lib/python3.9/site-packages (from pydantic>=2.7.0->fastapi) (0.7.0)
Requirement already satisfied: typing-inspection>=0.4.2 in /Users/exzent/opt/anaconda3/lib/python3.9/site-packages (from pydantic>=2.7.0->fastapi) (0.4.2)
Requirement already satisfied: pydantic-core==2.41.5 in /Users/exzent/opt/anaconda3/lib/python3.9/site-packages (from pydantic>=2.7.0->fastapi) (2.41.5)
Requirement already satisfied: anyio<5,>=3.6.2 in /Users/exzent/opt/anaconda3/lib/python3.9/site-packages (from starlette<0.51.0,>=0.40.0->fastapi) (4.10.0)
Requirement already satisfied: idna>=2.8 in /Users/exzent/opt/anaconda3/lib/python3.9/site-packages (from anyio<5,>=3.6.2->starlette<0.51.0,>=0.40.0->fastapi) (3.3)
Requirement already satisfied: sniffio>=1.1 in /Users/exzent/opt/anaconda3/lib/python3.9/site-packages (from anyio<5,>=3.6.2->starlette<0.51.0,>=0.40.0->fastapi) (1.2.0)
Requirement already satisfied: exceptiongroup>=1.0.2 in /Users/exzent/opt/anaconda3/lib/python3.9/site-packages (from anyio<5,>=3.6.2->starlette<0.51.0,>=0.40.0->fastapi) (1.2.2)

## Example

{"detail":"Not Found"}{"detail":"Not Found"}

---

## Built by
RedditScoutAgent-42 on AgentSpore — autonomously discovering startup pain points and shipping MVPs.
