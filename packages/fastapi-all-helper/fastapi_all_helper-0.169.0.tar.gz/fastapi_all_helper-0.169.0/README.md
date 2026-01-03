# 🚀 FastAPI Helper

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.127%2B-green.svg)](https://fastapi.tiangolo.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%2B-orange.svg)](https://sqlalchemy.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PyPI](https://img.shields.io/badge/PyPI-fastapi--helper-blue.svg)](https://pypi.org/project/fastapi-helper)

# 📥 Installation
```bash
pip install fastapi-all-helper
```

# ✅ Quick Start
```python
import asyncio
from fastapi import FastAPI
from fastapi_helper import Client


app = FastAPI()
client = Client(app)


async def main() -> None:
    await client.start_app()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        await client.stop_app()
```



