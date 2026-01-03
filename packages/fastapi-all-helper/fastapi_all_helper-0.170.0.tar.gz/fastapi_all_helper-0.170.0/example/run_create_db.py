import asyncio

from fastapi_helper.sql import DataBaseHelper

db_helper = DataBaseHelper(
    url="sqlite+aiosqlite:///test.db"
)


async def main() -> None:
    await db_helper.init_db()
    
    
async def run_code():
    await main()
    await db_helper.dispose()
    
if __name__ == "__main__":
    asyncio.run(run_code())
