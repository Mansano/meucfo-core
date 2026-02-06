# app/repositories/pricing_data.py

from typing import List, Optional
from datetime import datetime
from app.d1_client import execute_sql
from app.models.pricing import PricingCalculationRequest

class PricingDataRepository:
    @staticmethod
    async def create_calculation(user_id: int, request: PricingCalculationRequest, result: dict) -> Optional[int]:
        sql = """
        INSERT INTO pricing_data (
            user_id, business_type, product_cost, shipping_insurance,
            icms_purchase_percent, ipi_percent, variable_expenses,
            fixed_expenses_percent, sale_taxes_percent, net_profit_percent,
            product_type, tax_regime, origin_state, destination_state,
            calculated_price, margin
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = [
            user_id,
            request.business_type.value,
            request.product_cost,
            request.shipping_insurance,
            request.icms_purchase_percent,
            request.ipi_percent,
            request.variable_expenses,
            request.fixed_expenses_percent,
            request.sale_taxes_percent,
            request.net_profit_percent,
            request.product_type.value,
            request.tax_regime.value,
            request.origin_state,
            request.destination_state,
            result.get('calculated_price'),
            result.get('margin')
        ]
        
        db_result = await execute_sql(sql, params)
        
        if db_result.get("success"):
            return db_result.get("meta", {}).get("last_row_id")
        return None
    
    @staticmethod
    async def get_user_calculations(user_id: int, limit: int = 50) -> List[dict]:
        result = await execute_sql(
            """
            SELECT * FROM pricing_data 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
            """,
            [user_id, limit]
        )
        
        if result.get("success") and result.get("results"):
            return result["results"]
        return []
    
    @staticmethod
    async def get_calculation_by_id(calc_id: int, user_id: Optional[int] = None) -> Optional[dict]:
        if user_id:
            sql = "SELECT * FROM pricing_data WHERE id = ? AND user_id = ?"
            params = [calc_id, user_id]
        else:
            sql = "SELECT * FROM pricing_data WHERE id = ?"
            params = [calc_id]
        
        result = await execute_sql(sql, params)
        
        if result.get("success") and result.get("results"):
            return result["results"][0]
        return None
