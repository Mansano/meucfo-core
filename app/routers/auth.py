# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from app.models.user import UserCreate, UserLogin, Token, UserResponse
from app.repositories.users import UserRepository
from app.services.auth import (
    hash_password, verify_password, create_access_token, verify_token
)
from app.rate_limit import RateLimiter
from app.config import settings

router = APIRouter()
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Obtém o usuário atual do token JWT"""
    token = credentials.credentials
    token_data = verify_token(token)
    
    return {
        "user_id": token_data.user_id,
        "email": token_data.email,
        "is_admin": token_data.is_admin
    }

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, request: Request):
    """Registro de novo usuário"""
    
    # Verificar se usuário já existe
    existing_user = await UserRepository.get_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já registrado"
        )
    
    # Criar hash da senha
    password_hash = hash_password(user_data.password)
    
    # Criar usuário
    user_id = await UserRepository.create({
        "email": user_data.email,
        "password": password_hash,
        "name": user_data.name or user_data.full_name, # Fallback compatibilidade
        "company_name": user_data.company_name,
        "phone": user_data.phone,
        "is_approved": False  # Requer aprovação do admin
    })
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar usuário"
        )
    
    # Obter usuário criado
    user = await UserRepository.get_by_id(user_id)
    
    # Log de registro
    client_ip = request.client.host if request.client else "unknown"
    print(f"Novo usuário registrado: {user.email} from {client_ip}")
    
    return user

@router.post("/login", response_model=Token)
async def login(login_data: UserLogin, request: Request):
    """Login de usuário"""
    # Rate limiting
    redis_client = request.app.state.redis
    rate_limiter = RateLimiter(redis_client)
    
    client_ip = request.client.host if request.client else "unknown"
    identifier = f"{client_ip}:{login_data.email}"
    
    # Verificar se excedeu limite de tentativas
    allowed, remaining_time = await rate_limiter.check_login_limit(identifier)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Muitas tentativas de login. Tente novamente em {remaining_time} segundos."
        )
    
    # Buscar usuário
    user = await UserRepository.get_by_email(login_data.email)
    if not user:
        await rate_limiter.record_login_attempt(identifier)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )
    
    # Verificar senha
    if not verify_password(login_data.password, user.password):
        await rate_limiter.record_login_attempt(identifier)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )
    
    # Verificar se usuário está aprovado
    if not user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário aguardando aprovação do administrador"
        )
    
    # Resetar contador de tentativas
    await rate_limiter.reset_login_attempts(identifier)
    
    # Atualizar último login
    await UserRepository.update_login_time(user.id)
    
    # Criar token
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.id,
            "is_admin": user.is_admin
        }
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user
    )

@router.post("/logout")
async def logout(request: Request, current_user: dict = Depends(get_current_user)):
    """Logout de usuário"""
    # Em implementação JWT com cookies, invalidar o token
    # Para esta implementação, o frontend deve remover o token
    return {"message": "Logout realizado com sucesso"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Obtém informações do usuário atual"""
    user = await UserRepository.get_by_id(current_user["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    return user
