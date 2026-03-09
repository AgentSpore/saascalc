from pydantic import BaseModel
from typing import Optional


class LTVInput(BaseModel):
    arpu: float                      # average revenue per user (monthly)
    churn_rate_pct: float            # monthly churn %
    gross_margin_pct: float = 100.0  # optional gross margin %


class CACInput(BaseModel):
    total_sales_marketing_spend: float
    new_customers_acquired: int


class MRRInput(BaseModel):
    customers: int
    arpu: float  # average monthly revenue per customer


class RunwayInput(BaseModel):
    cash_on_hand: float
    monthly_burn: float


class PaybackInput(BaseModel):
    cac: float
    arpu: float               # monthly
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


class FullMetricsInput(BaseModel):
    arpu: float
    churn_rate_pct: float
    gross_margin_pct: float
    total_sales_marketing_spend: float
    new_customers_acquired: int
    cash_on_hand: float
    monthly_burn: float
    mrr: float
