# app/d1_client.py

import os
import json
import logging
from typing import List, Dict, Any, Optional
import httpx
from datetime import datetime

from app.config import settings

logger = logging.getLogger(__name__)

class D1Client:
    def __init__(self):
        # Strip whitespace, quotes (single/double), and slashes from IDs
        self.account_id = settings.CLOUDFLARE_ACCOUNT_ID.strip().strip("'").strip('"').strip("/")
        self.database_id = settings.CLOUDFLARE_DATABASE_ID.strip().strip("'").strip('"').strip("/")
        self.api_token = settings.CLOUDFLARE_API_TOKEN.strip().strip("'").strip('"')
        
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/d1/database/{self.database_id}"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        # Log REPR to see invisible characters
        logger.info(f"D1 Client URL REPR: {repr(self.base_url)}")

    async def execute(self, sql: str, params: Optional[List] = None) -> Dict[str, Any]:
        """Executa uma query SQL no D1"""
        # Sempre enviar params como lista, mesmo que vazia
        safe_params = params if params is not None else []
        
        payload = {
            "sql": sql,
            "params": safe_params
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # Log Payload (debug)
                logger.info(f"D1 Executing. Payload: {json.dumps(payload)}")
                
                response = await client.post(
                    f"{self.base_url}/query",
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code >= 400:
                    logger.error(f"D1 Error Status: {response.status_code}")
                    logger.error(f"D1 Error Body: {response.text}")
                    return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                
                result = response.json()
                
                if not result.get("success"):
                    logger.error(f"Erro no D1: {result.get('errors', [])}")
                    return {"success": False, "errors": result.get("errors", [])}
                
                return result.get("result", [])[0] if result.get("result") else {}
                
            except Exception as e:
                logger.error(f"Erro ao executar query no D1: {str(e)}")
                return {"success": False, "error": str(e)}
    
    async def execute_many(self, sql: str, params_list: List[List]) -> Dict[str, Any]:
        """Executa múltiplas queries em batch"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/query",
                    headers=self.headers,
                    json={
                        "sql": sql,
                        "params": params_list
                    }
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Erro ao executar batch no D1: {str(e)}")
                return {"success": False, "error": str(e)}

# Instância global
d1_client = D1Client()

async def execute_sql(sql: str, params: Optional[List] = None) -> Dict[str, Any]:
    """Função helper para executar SQL"""
    return await d1_client.execute(sql, params)

async def init_db():
    """Inicializa o banco de dados criando tabelas se não existirem"""
    
    # Tabela de usuários
    users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT,
        company_name TEXT,
        phone TEXT,
        is_admin INTEGER NOT NULL DEFAULT 0,
        is_approved INTEGER NOT NULL DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now')),
        last_login TEXT,
        metadata TEXT DEFAULT '{}'
    )
    """
    
    # Tabela de preços (para dashboard financeiro)
    prices_table = """
    CREATE TABLE IF NOT EXISTS prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        date TEXT NOT NULL,
        close REAL NOT NULL,
        volume INTEGER,
        created_at TEXT DEFAULT (datetime('now')),
        UNIQUE(symbol, date)
    )
    """
    
    # Tabela de dados de precificação
    pricing_data_table = """
    CREATE TABLE IF NOT EXISTS pricing_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        business_type TEXT NOT NULL,
        product_cost REAL NOT NULL,
        shipping_insurance REAL DEFAULT 0,
        icms_purchase_percent REAL DEFAULT 0,
        ipi_percent REAL DEFAULT 0,
        variable_expenses REAL DEFAULT 0,
        fixed_expenses_percent REAL DEFAULT 0,
        sale_taxes_percent REAL DEFAULT 0,
        net_profit_percent REAL DEFAULT 0,
        product_type TEXT,
        tax_regime TEXT,
        origin_state TEXT,
        destination_state TEXT,
        calculated_price REAL,
        margin REAL,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """
    
    # Tabela de análise competitiva
    competitive_analysis_table = """
    CREATE TABLE IF NOT EXISTS competitive_analysis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        business_data TEXT NOT NULL,
        products_data TEXT NOT NULL,
        sales_history TEXT NOT NULL,
        cost_structure TEXT NOT NULL,
        suppliers_data TEXT NOT NULL,
        analysis_results TEXT,
        webhook_response TEXT,
        status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """
    
    # Tabela de logs de webhook
    webhook_logs_table = """
    CREATE TABLE IF NOT EXISTS webhook_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        webhook_type TEXT NOT NULL,
        payload TEXT NOT NULL,
        response TEXT,
        status_code INTEGER,
        created_at TEXT DEFAULT (datetime('now'))
    )
    """
    
    tables = [
        users_table,
        prices_table,
        pricing_data_table,
        competitive_analysis_table,
        webhook_logs_table
    ]
    
    for table_sql in tables:
        result = await execute_sql(table_sql)
        if not result.get("success"):
            logger.warning(f"Erro ao criar tabela: {result.get('error')}")
    
    # Criar usuário admin padrão se não existir
    from app.services.auth import hash_password
    admin_check = await execute_sql(
        "SELECT id FROM users WHERE email = ?",
        [settings.APP_ADMIN_MAIL]
    )
    
    if admin_check.get("success") and not admin_check.get("results"):
        admin_pass_hash = hash_password(settings.APP_ADMIN_PASS)
        await execute_sql(
            """
            INSERT INTO users (email, password_hash, full_name, is_admin, is_approved)
            VALUES (?, ?, ?, 1, 1)
            """,
            [settings.APP_ADMIN_MAIL, admin_pass_hash, "Administrador"]
        )
        logger.info("Usuário admin criado com sucesso")
    
    logger.info("Banco de dados inicializado com sucesso")
