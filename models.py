from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CalculationInput(BaseModel):
    """Reject nonfinite numbers consistently across calculator inputs."""

    model_config = ConfigDict(allow_inf_nan=False)


class LTVInput(CalculationInput):
    arpu: float = Field(..., gt=0)
    churn_rate_pct: float = Field(..., gt=0, le=100)
    gross_margin_pct: float = Field(100.0, ge=0, le=100)


class CACInput(CalculationInput):
    total_sales_marketing_spend: float = Field(..., ge=0)
    new_customers_acquired: int = Field(..., gt=0)


class MRRInput(CalculationInput):
    customers: int = Field(..., ge=0)
    arpu: float = Field(..., ge=0)


class RunwayInput(CalculationInput):
    cash_on_hand: float = Field(..., ge=0)
    monthly_burn: float = Field(..., ge=0)


class PaybackInput(CalculationInput):
    cac: float = Field(..., ge=0)
    arpu: float = Field(..., gt=0)
    gross_margin_pct: float = Field(100.0, gt=0, le=100)


class ChurnInput(CalculationInput):
    customers_start: int = Field(..., gt=0)
    customers_lost: int = Field(..., ge=0)
    period_days: int = Field(30, gt=0)

    @model_validator(mode="after")
    def validate_customer_loss(self) -> Self:
        """Require lost customers to be part of the starting cohort."""
        if self.customers_lost > self.customers_start:
            raise ValueError("customers_lost must not exceed customers_start")
        return self


class ARRInput(CalculationInput):
    mrr: float


class QuickRatioInput(CalculationInput):
    new_mrr: float = Field(..., ge=0)
    expansion_mrr: float = Field(..., ge=0)
    churned_mrr: float = Field(..., ge=0)
    contraction_mrr: float = Field(..., ge=0)


class NDRInput(CalculationInput):
    mrr_start: float = Field(..., gt=0)
    expansion_mrr: float = Field(..., ge=0)
    contraction_mrr: float = Field(..., ge=0)
    churned_mrr: float = Field(..., ge=0)

    @model_validator(mode="after")
    def validate_ending_revenue(self) -> Self:
        """Require revenue losses to fit the starting revenue plus expansion."""
        if (
            self.contraction_mrr + self.churned_mrr
            > self.mrr_start + self.expansion_mrr
        ):
            raise ValueError(
                "contraction_mrr and churned_mrr must not exceed mrr_start plus expansion_mrr"
            )
        return self


class RuleOf40Input(CalculationInput):
    revenue_growth_rate_pct: float
    profit_margin_pct: float


class FullMetricsInput(CalculationInput):
    arpu: float = Field(..., gt=0)
    churn_rate_pct: float = Field(..., gt=0, le=100)
    gross_margin_pct: float = Field(..., gt=0, le=100)
    total_sales_marketing_spend: float = Field(..., ge=0)
    new_customers_acquired: int = Field(..., gt=0)
    cash_on_hand: float = Field(..., ge=0)
    monthly_burn: float = Field(..., ge=0)
    mrr: float = Field(..., ge=0)


class CompareInput(CalculationInput):
    period_a_label: str = Field("Period A", max_length=50)
    period_b_label: str = Field("Period B", max_length=50)
    period_a: FullMetricsInput
    period_b: FullMetricsInput
