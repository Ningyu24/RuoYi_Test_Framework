# testcases/conftest.py
import time

import pytest
from common.http_client import HttpClient
from common.db_client import DbClient



@pytest.fixture(scope="session")
def api_client():
    """返回 HttpClient 类，供测试用例使用"""
    return HttpClient

@pytest.fixture
def unique_username():
    """生成唯一用户名"""
    return f"auto_{int(time.time_ns())}"

@pytest.fixture
def db_client():
    return DbClient