# app/routers/pricing.py

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List
import os

from app.models.pricing import PricingCalculationRequest, PricingCalculationResponse
from app.services.pricing_calculator import PricingCalculatorService
from app.repositories.pricing_data import PricingDataRepository
from app.routers.auth import get_current_user
from app.utils.webhook import send_webhook
from app.config import settings

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/calculator", response_class=HTMLResponse, name="pricing_calculator")
async def get_calculator(request: Request):
    """Renderiza a página da calculadora de precificação"""
    return templates.TemplateResponse(
        "calculator.html",
        {"request": request, "title": "Calculadora de Precificação - MeuCFO.ai", "current_user": None}
    )

@router.post("/calculate", response_model=PricingCalculationResponse)
async def calculate_price(
    request: PricingCalculationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Calcula preço de venda baseado nos parâmetros"""
    
    # Calcular preço
    result = PricingCalculatorService.calculate_price(request)
    
    # Salvar cálculo no banco
    calc_id = await PricingDataRepository.create_calculation(
        current_user["user_id"], request, result.dict()
    )
    
    # Enviar para webhook para análise adicional
    webhook_data = {
        "calculation_id": calc_id,
        "user_id": current_user["user_id"],
        "request": request.dict(),
        "result": result.dict()
    }
    
    # Enviar assincronamente (não bloquear resposta)
    import asyncio
    asyncio.create_task(
        send_webhook(
            "pricing_calculation",
            webhook_data,
            settings.N8N_WEBHOOK_URL
        )
    )
    
    return result

@router.get("/calculations")
async def get_user_calculations(
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Obtém histórico de cálculos do usuário"""
    calculations = await PricingDataRepository.get_user_calculations(
        current_user["user_id"], limit
    )
    
    return {
        "calculations": calculations,
        "count": len(calculations)
    }

@router.get("/calculations/{calc_id}")
async def get_calculation(
    calc_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Obtém um cálculo específico"""
    calculation = await PricingDataRepository.get_calculation_by_id(
        calc_id, current_user["user_id"]
    )
    
    if not calculation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cálculo não encontrado"
        )
    
    return calculation

@router.post("/simulate")
async def simulate_price_changes(
    base_request: PricingCalculationRequest,
    variations: List[dict],
    current_user: dict = Depends(get_current_user)
):
    """Simula variações nos parâmetros de cálculo"""
    
    simulations = []
    
    for variation in variations:
        # Criar cópia da requisição base
        import copy
        sim_request = copy.deepcopy(base_request)
        
        # Aplicar variações
        for key, value in variation.items():
            if hasattr(sim_request, key):
                setattr(sim_request, key, value)
        
        # Calcular
        result = PricingCalculatorService.calculate_price(sim_request)
        
        simulations.append({
            "variation": variation,
            "result": result.dict()
        })
    
    return {
        "base_result": PricingCalculatorService.calculate_price(base_request).dict(),
        "simulations": simulations,
        "variation_analysis": _analyze_variations(simulations)
    }

def _analyze_variations(simulations: List[dict]) -> dict:
    """Analisa o impacto das variações"""
    if not simulations:
        return {}
    
    analysis = {
        "most_sensitive_parameter": None,
        "max_price_variation": 0,
        "max_margin_variation": 0,
        "recommendations": []
    }
    
    # Análise simplificada
    price_changes = []
    margin_changes = []
    
    for sim in simulations:
        base_price = sim["result"]["calculated_price"]
        base_margin = sim["result"]["margin"]
        
        # Aqui você pode comparar com o resultado base
        # Implementação completa depende do contexto
        
        price_changes.append(abs(base_price))
        margin_changes.append(abs(base_margin))
    
    if price_changes:
        analysis["max_price_variation"] = max(price_changes)
        analysis["max_margin_variation"] = max(margin_changes)
    
    return analysis
