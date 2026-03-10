from pydantic import BaseModel, Field
from typing import Optional


class LTVInput(BaseModel):
    arpu: float = Field(..., gt=0)
    churn_rate_pct: float = Field(..., gt=0, le=100)
    gross_margin_pct: float = Field(100.0, ge=0, le=100)


class CACInput(BaseModel):
    total_sales_marketing_spend: float = Field(..., ge=0)
    new_customers_acquired: int = Field(..., gt=0)


class MRRInput(BaseModel):
    customers: int = Field(..., ge=0)
    arpu: float = Field(..., ge=0)


class RunwayInput(BaseModel):
    cash_on_hand: float = Field(..., ge=0)
    monthly_burn: float = Field(..., ge=0)


class PaybackInput(BaseModel):
    cac: float = Field(..., ge=0)
    arpu: float = Field(..., gt=0)
    gross_margin_pct: float = Field(100.0, gt=0, le=100)


class ChurnInput(BaseModel):
    customers_start: int = Field(..., gt=0)
    customers_lost: int = Field(..., ge=0)
    period_days: int = Field(30, gt=0)


class ARRInput(BaseModel):
    mrr: float


class QuickRatioInput(BaseModel):
    new_mrr: float = Field(..., ge=0)
    expansion_mrr: float = Field(..., ge=0)
    churned_mrr: float = Field(..., ge=0)
    contraction_mrr: float = Field(..., ge=0)


class NDRInput(BaseModel):
    mrr_start: float = Field(..., gt=0)
    expansion_mrr: float = Field(..., ge=0)
    contraction_mrr: float = Field(..., ge=0)
    churned_mrr: float = Field(..., ge=0)


class RuleOf40Input(BaseModel):
    revenue_growth_rate_pct: float
    profit_margin_pct: float


class FullMetricsInput(BaseModel):
    arpu: float = Field(..., gt=0)
    churn_rate_pct: float = Field(..., gt=0, le=100)
    gross_margin_pct: float = Field(..., gt=0, le=100)
    total_sales_marketing_spend: float = Field(..., ge=0)
    new_customers_acquired: int = Field(..., gt=0)
    cash_on_hand: float = Field(..., ge=0)
    monthly_burn: float = Field(..., ge=0)
    mrr: float = Field(..., ge=0)


class CompareInput(BaseModel):
    period_a_label: str = Field("Period A", max_length=50)
    period_b_label: str = Field("Period B", max_length=50)
    period_a: FullMetricsInput
    period_b: FullMetricsInput
