# app/routers/dashboard.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/settings")
async def dashboard_settings():
    return {"message": "Dashboard settings"}

# Adicionar endpoint /metrics usado no JS
@router.get("/metrics")
async def dashboard_metrics():
    return {
        "success": True,
        "metrics": {
            "net_margin": 15.2,
            "monthly_revenue": 102500.00,
            "stock_turnover": 4.2,
            "operational_costs": 45000.00
        },
        "chart_data": {
            "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "revenue": [80000, 85000, 90000, 95000, 92000, 102500],
            "profit": [12000, 15000, 18000, 20000, 19000, 25000]
        }
    }
