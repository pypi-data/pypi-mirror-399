import asyncio

from fastapi import FastAPI

from fastapi_helper import Client

app = FastAPI()
client = Client(app)


async def main():
    await client.start_app()
    
    
if __name__ == "__main__":
    asyncio.run(main())
