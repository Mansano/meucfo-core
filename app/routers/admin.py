# app/routers/admin.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def admin_home():
    return {"message": "Admin area"}
