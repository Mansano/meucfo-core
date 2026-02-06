# app/models/pricing.py

from pydantic import BaseModel, field_validator
from typing import Optional, Literal
from enum import Enum

class BusinessType(str, Enum):
    RETAIL = "varejo"
    SERVICE = "servicos"

class TaxRegime(str, Enum):
    SIMPLES_NACIONAL = "simples_nacional"
    LUCRO_PRESUMIDO = "lucro_presumido"
    LUCRO_REAL = "lucro_real"

class ProductType(str, Enum):
    ALIMENTICIO = "alimenticio"
    ELETRONICOS = "eletronicos"
    VESTUARIO = "vestuario"
    FARMACIA = "farmacia"
    SERVICOS = "servicos"
    OUTROS = "outros"

class PricingCalculationRequest(BaseModel):
    business_type: BusinessType
    product_cost: float
    shipping_insurance: float = 0.0
    icms_purchase_percent: float = 0.0
    ipi_percent: float = 0.0
    variable_expenses: float = 0.0
    fixed_expenses_percent: float = 0.0
    sale_taxes_percent: float = 0.0
    net_profit_percent: float = 0.0
    product_type: ProductType
    tax_regime: TaxRegime
    origin_state: str
    destination_state: str
    
    @field_validator('product_cost', 'shipping_insurance', 'net_profit_percent')
    def positive_values(cls, v, info):
        if v < 0:
            raise ValueError(f'{info.field_name} deve ser um valor positivo')
        return v
    
    @field_validator('icms_purchase_percent', 'ipi_percent', 'fixed_expenses_percent', 
               'sale_taxes_percent', 'variable_expenses')
    def percent_range(cls, v, info):
        if v < 0 or v > 100:
            raise ValueError(f'{info.field_name} deve estar entre 0 e 100')
        return v

class PricingCalculationResponse(BaseModel):
    calculated_price: float
    margin: float
    cost_breakdown: dict
    recommendations: list[str]
    tax_impact: dict
