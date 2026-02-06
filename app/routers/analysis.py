# app/routers/analysis.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/competitive")
async def competitive_analysis():
    # Isso deveria retornar html se for acessado pelo navegador ou json se api
    return {"message": "Competitive analysis"}
