# app/models/analysis.py

from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import date

class BusinessData(BaseModel):
    informacoes_gerais: Dict[str, Any]
    produtos: List[Dict[str, Any]]
    vendas_historicas: List[Dict[str, Any]]
    estrutura_custos: Dict[str, Any]
    fornecedores: List[Dict[str, Any]]

class CompetitiveAnalysisRequest(BaseModel):
    business_data: BusinessData
    analysis_type: str = "complete"
    include_forecast: bool = True
    timeframe_months: int = 36

class AnalysisResults(BaseModel):
    profitability_analysis: Dict[str, Any]
    competitive_analysis: Dict[str, Any]
    tax_optimization: Dict[str, Any]
    operational_efficiency: Dict[str, Any]
    financial_projections: Dict[str, Any]
    recommendations: List[str]
    risk_assessment: Dict[str, Any]
