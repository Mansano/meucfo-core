# app/rate_limit.py

import redis.asyncio as redis
from typing import Optional, Tuple
import time
from app.config import settings

class RateLimiter:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def check_login_limit(self, identifier: str, max_attempts: int = None, window: int = None) -> Tuple[bool, Optional[int]]:
        """
        Verifica se o login excedeu o limite de tentativas.
        Retorna (allowed, remaining_time)
        """
        max_attempts = max_attempts or settings.RATE_LIMIT_LOGIN_ATTEMPTS
        window = window or settings.RATE_LIMIT_LOGIN_WINDOW
        
        key = f"login_attempts:{identifier}"
        
        # Obter tentativas atuais
        attempts = await self.redis.get(key)
        current_attempts = int(attempts) if attempts else 0
        
        if current_attempts >= max_attempts:
            # Calcular tempo restante do bloqueio
            ttl = await self.redis.ttl(key)
            if ttl > 0:
                return False, ttl
            else:
                # Se TTL expirou, resetar contador
                await self.redis.delete(key)
                return True, None
        
        return True, None
    
    async def record_login_attempt(self, identifier: str, max_attempts: int = None, window: int = None):
        """Registra uma tentativa de login"""
        max_attempts = max_attempts or settings.RATE_LIMIT_LOGIN_ATTEMPTS
        window = window or settings.RATE_LIMIT_LOGIN_WINDOW
        
        key = f"login_attempts:{identifier}"
        
        # Incrementar contador
        current = await self.redis.incr(key)
        
        # Se for a primeira tentativa, definir expiração
        if current == 1:
            await self.redis.expire(key, window)
        
        return current
    
    async def reset_login_attempts(self, identifier: str):
        """Reseta as tentativas de login para um identificador"""
        key = f"login_attempts:{identifier}"
        await self.redis.delete(key)
    
    async def check_api_limit(self, user_id: str, endpoint: str, max_calls: int = None, window: int = None) -> Tuple[bool, Optional[int]]:
        """Verifica limite de chamadas API"""
        max_calls = max_calls or settings.RATE_LIMIT_API_CALLS
        window = window or settings.RATE_LIMIT_API_WINDOW
        
        key = f"api_calls:{user_id}:{endpoint}:{int(time.time() // window)}"
        
        current_calls = await self.redis.incr(key)
        
        if current_calls == 1:
            await self.redis.expire(key, window)
        
        if current_calls > max_calls:
            ttl = await self.redis.ttl(key)
            return False, ttl
        
        return True, None

async def init_redis() -> redis.Redis:
    """Inicializa conexão Redis"""
    try:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            password=settings.REDIS_PASSWORD,
            username=settings.REDIS_USERNAME,
            decode_responses=True
        )
        
        # Testar conexão
        await redis_client.ping()
        return redis_client
    except Exception as e:
        raise Exception(f"Falha ao conectar ao Redis: {str(e)}")
