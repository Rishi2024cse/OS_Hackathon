import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("DATABASE_URL")
print(f"Testing URL: {url.replace('Charan%40021206', '***')}")

async def test():
    try:
        engine = create_async_engine(url)
        async with engine.connect() as conn:
            print("Successfully connected to Supabase!")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test())
