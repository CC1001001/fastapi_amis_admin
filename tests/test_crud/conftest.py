import datetime
from typing import AsyncGenerator, Any, List

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import insert
from sqlmodel import SQLModel

from tests.db import async_db as db
from tests.models import User

pytestmark = pytest.mark.asyncio


@pytest.fixture
def app() -> FastAPI:
    return FastAPI()


@pytest.fixture
async def prepare_database() -> AsyncGenerator[None, None]:
    await db.async_run_sync(SQLModel.metadata.create_all, is_session=False)
    yield
    await db.async_run_sync(SQLModel.metadata.drop_all, is_session=False)
    await db.engine.dispose()


@pytest.fixture
async def async_client(app: FastAPI, prepare_database: Any) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://testserver") as c:
        yield c


@pytest.fixture
async def fake_users() -> List[User]:
    data = [
        {'id': i,
         "username": f'User_{i}',
         "password": f"password_{i}",
         "create_time": datetime.datetime.strptime(f"2022-01-0{i} 00:00:00", "%Y-%m-%d %H:%M:%S")
         } for i in range(1, 6)
    ]
    await db.execute(insert(User).values(data), commit=True)
    return [User.parse_obj(item) for item in data]
