import asyncio
import os
import httpx
from dotenv import load_dotenv

async def test_connection():
    load_dotenv()
    
    # Read raw
    raw_account = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
    raw_db = os.getenv("CLOUDFLARE_DATABASE_ID", "")
    raw_token = os.getenv("CLOUDFLARE_API_TOKEN", "")
    
    print(f"--- DEBUG INFO ---")
    print(f"Raw Account ID len: {len(raw_account)}")
    print(f"Raw DB ID len: {len(raw_db)}")
    
    # Sanitize
    account_id = raw_account.strip().strip("'").strip('"').strip("/")
    database_id = raw_db.strip().strip("'").strip('"').strip("/")
    api_token = raw_token.strip().strip("'").strip('"')
    
    print(f"Sanitized Account ID: {account_id}")
    print(f"Sanitized DB ID: {database_id}")
    print(f"Token (first 4): {api_token[:4]}")
    
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/d1/database/{database_id}/query"
    
    print(f"Target URL: {url}")
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "sql": "PRAGMA table_info(users);",
        "params": []
    }
    
    print("Sending request...")
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, headers=headers, json=payload)
            print(f"Status Code: {resp.status_code}")
            print(f"Response Body: {resp.text}")
        except Exception as e:
            print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
