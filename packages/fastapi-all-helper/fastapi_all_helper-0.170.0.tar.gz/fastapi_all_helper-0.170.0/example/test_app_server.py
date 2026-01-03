import asyncio

from fastapi import FastAPI
from fastapi_helper import Client
from fastapi_helper.pj import gpt_router


app = FastAPI()
client = Client(app, "127.0.0.1", 9090, True)

app.include_router(gpt_router)


async def main() -> None:
    await client.start_app(certfile="certs/cert.pem", keyfile="certs/key.pem")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass