from pydantic import BaseModel
from typing import Optional


class LTVInput(BaseModel):
    arpu: float
    churn_rate_pct: float
    gross_margin_pct: float = 100.0


class CACInput(BaseModel):
    total_sales_marketing_spend: float
    new_customers_acquired: int


class MRRInput(BaseModel):
    customers: int
    arpu: float


class RunwayInput(BaseModel):
    cash_on_hand: float
    monthly_burn: float


class PaybackInput(BaseModel):
    cac: float
    arpu: float
    gross_margin_pct: float = 100.0


class ChurnInput(BaseModel):
    customers_start: int
    customers_lost: int
    period_days: int = 30


class ARRInput(BaseModel):
    mrr: float


class QuickRatioInput(BaseModel):
    new_mrr: float
    expansion_mrr: float
    churned_mrr: float
    contraction_mrr: float


class NDRInput(BaseModel):
    mrr_start: float              # MRR at start of period (existing customers only)
    expansion_mrr: float          # Upsells / seat expansions
    contraction_mrr: float        # Downgrades
    churned_mrr: float            # Cancelled accounts


class RuleOf40Input(BaseModel):
    revenue_growth_rate_pct: float    # YoY or QoQ revenue growth %
    profit_margin_pct: float          # EBITDA or FCF margin % (negative = burning cash)


class FullMetricsInput(BaseModel):
    arpu: float
    churn_rate_pct: float
    gross_margin_pct: float
    total_sales_marketing_spend: float
    new_customers_acquired: int
    cash_on_hand: float
    monthly_burn: float
    mrr: float
