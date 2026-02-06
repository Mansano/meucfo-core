# app/services/pricing_calculator.py

from typing import Dict, Any
from app.models.pricing import PricingCalculationRequest, PricingCalculationResponse

class PricingCalculatorService:
    @staticmethod
    def calculate_price(request: PricingCalculationRequest) -> PricingCalculationResponse:
        """Calcula o preço de venda baseado nos parâmetros fornecidos"""
        
        # Cálculo do custo total
        total_cost = request.product_cost
        
        # Adicionar frete e seguro
        total_cost += request.shipping_insurance
        
        # Adicionar ICMS na compra (se aplicável)
        icms_purchase = total_cost * (request.icms_purchase_percent / 100)
        
        # Adicionar IPI (se aplicável)
        ipi_value = (total_cost + icms_purchase) * (request.ipi_percent / 100)
        
        # Custo com impostos de compra
        cost_with_taxes = total_cost + icms_purchase + ipi_value
        
        # Adicionar despesas variáveis
        variable_expenses_value = cost_with_taxes * (request.variable_expenses / 100)
        
        # Custo com despesas variáveis
        cost_with_variable = cost_with_taxes + variable_expenses_value
        
        # Calcular preço de venda considerando margem desejada
        # Fórmula: Preço = Custo / (1 - (%Despesas Fixas + %Tributos Venda + %Lucro))
        total_percentages = (
            request.fixed_expenses_percent + 
            request.sale_taxes_percent + 
            request.net_profit_percent
        ) / 100
        
        if total_percentages >= 1:
            # Se as porcentagens somam 100% ou mais, ajustar
            total_percentages = 0.9  # Limitar a 90%
        
        calculated_price = cost_with_variable / (1 - total_percentages)
        
        # Calcular margem líquida real
        # Receita líquida = Preço - Tributos sobre venda - Despesas fixas
        sale_taxes_value = calculated_price * (request.sale_taxes_percent / 100)
        fixed_expenses_value = calculated_price * (request.fixed_expenses_percent / 100)
        
        net_revenue = calculated_price - sale_taxes_value - fixed_expenses_value - cost_with_variable
        margin = (net_revenue / calculated_price) * 100 if calculated_price > 0 else 0
        
        # Estrutura de detalhamento
        cost_breakdown = {
            "custo_produto": request.product_cost,
            "frete_seguro": request.shipping_insurance,
            "icms_compra": icms_purchase,
            "ipi": ipi_value,
            "despesas_variaveis": variable_expenses_value,
            "custo_total": cost_with_variable,
            "despesas_fixas": fixed_expenses_value,
            "tributos_venda": sale_taxes_value,
            "receita_liquida": net_revenue
        }
        
        # Recomendações baseadas no cálculo
        recommendations = []
        
        if margin < request.net_profit_percent * 0.8:
            recommendations.append(
                "A margem calculada está abaixo da desejada. Considere: "
                "1. Negociar melhor com fornecedores\n"
                "2. Reduzir despesas variáveis\n"
                "3. Revisar estrutura de custos fixos"
            )
        
        if request.sale_taxes_percent > 15:
            recommendations.append(
                "A carga tributária está elevada. Considere:\n"
                "1. Avaliar mudança de regime tributário\n"
                "2. Verificar benefícios fiscais do segmento\n"
                "3. Consultar especialista tributário"
            )
        
        # Impacto tributário detalhado
        tax_impact = {
            "icms_interestadual": PricingCalculatorService._calculate_icms_interestadual(
                request.origin_state, request.destination_state
            ),
            "regime_tributario": request.tax_regime.value,
            "aliquotas_aplicaveis": {
                "icms": request.icms_purchase_percent,
                "ipi": request.ipi_percent,
                "pis_cofins": 3.65,  # Média para maioria dos produtos
                "iss": 5.0 if request.business_type.value == "servicos" else 0
            }
        }
        
        return PricingCalculationResponse(
            calculated_price=round(calculated_price, 2),
            margin=round(margin, 2),
            cost_breakdown={k: round(v, 2) for k, v in cost_breakdown.items()},
            recommendations=recommendations,
            tax_impact=tax_impact
        )
    
    @staticmethod
    def _calculate_icms_interestadual(origin: str, destination: str) -> float:
        """Calcula diferença de ICMS interestadual"""
        # Tabela simplificada de alíquotas interestaduais
        icms_table = {
            "SP": {"SP": 18, "RJ": 12, "MG": 12, "PR": 12, "RS": 12, "Outros": 7},
            "RJ": {"RJ": 18, "SP": 12, "MG": 12, "Outros": 7},
            "MG": {"MG": 18, "SP": 12, "RJ": 12, "Outros": 7},
            "PR": {"PR": 18, "SP": 12, "SC": 12, "Outros": 7},
            # Adicionar outros estados conforme necessário
        }
        
        origin_data = icms_table.get(origin.upper(), {})
        rate = origin_data.get(destination.upper(), 7)
        
        return rate
