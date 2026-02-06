# app/repositories/users.py

from typing import Optional, List
from datetime import datetime
from app.d1_client import execute_sql
from app.models.user import UserInDB

class UserRepository:
    @staticmethod
    async def get_by_email(email: str) -> Optional[UserInDB]:
        result = await execute_sql(
            "SELECT * FROM users WHERE email = ?",
            [email]
        )
        
        if result.get("success") and result.get("results"):
            user_data = result["results"][0]
            return UserInDB(**user_data)
        return None
    
    @staticmethod
    async def get_by_id(user_id: int) -> Optional[UserInDB]:
        result = await execute_sql(
            "SELECT * FROM users WHERE id = ?",
            [user_id]
        )
        
        if result.get("success") and result.get("results"):
            user_data = result["results"][0]
            return UserInDB(**user_data)
        return None
    
    @staticmethod
    async def create(user_data: dict) -> Optional[int]:
        sql = """
        INSERT INTO users (email, password, full_name, company_name, phone, is_admin, is_approved)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        params = [
            user_data['email'],
            user_data['password'],
            user_data.get('full_name'),
            user_data.get('company_name'),
            user_data.get('phone'),
            user_data.get('is_admin', 0),
            user_data.get('is_approved', 0)
        ]
        
        result = await execute_sql(sql, params)
        
        if result.get("success"):
            return result.get("meta", {}).get("last_row_id")
        return None
    
    @staticmethod
    async def update_login_time(user_id: int):
        await execute_sql(
            "UPDATE users SET last_login = datetime('now') WHERE id = ?",
            [user_id]
        )
    
    @staticmethod
    async def get_pending_approvals() -> List[UserInDB]:
        result = await execute_sql(
            "SELECT * FROM users WHERE is_approved = 0 ORDER BY created_at DESC"
        )
        
        users = []
        if result.get("success") and result.get("results"):
            for user_data in result["results"]:
                users.append(UserInDB(**user_data))
        return users
    
    @staticmethod
    async def approve_user(user_id: int) -> bool:
        result = await execute_sql(
            "UPDATE users SET is_approved = 1 WHERE id = ?",
            [user_id]
        )
        return result.get("success", False)
    
    @staticmethod
    async def reject_user(user_id: int) -> bool:
        result = await execute_sql(
            "DELETE FROM users WHERE id = ? AND is_admin = 0",
            [user_id]
        )
        return result.get("success", False)
    
    @staticmethod
    async def get_all_users() -> List[UserInDB]:
        result = await execute_sql(
            "SELECT * FROM users ORDER BY created_at DESC"
        )
        
        users = []
        if result.get("success") and result.get("results"):
            for user_data in result["results"]:
                users.append(UserInDB(**user_data))
        return users
