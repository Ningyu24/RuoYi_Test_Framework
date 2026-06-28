import requests
import pymysql
import time
import pytest

# ======================== 配置 ========================
BASE_URL = "http://localhost:8080"
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "database": "ry-vue",
    "charset": "utf8mb4"
}

# ======================== 登录函数 ========================
def get_token():
    url = f"{BASE_URL}/login"
    payload = {"username": "admin", "password": "admin123"}
    resp = requests.post(url, json=payload)
    assert resp.status_code == 200
    token = resp.json().get("token")
    assert token is not None, "登录失败，未获取到 Token"
    return token

# ======================== 数据库查询工具 ========================
def query_db(sql):
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

# ======================== 测试类 ========================
class TestUserManagement:

    @pytest.fixture(scope="class")
    def token(self):
        """整个测试类只登录一次，复用 Token"""
        return get_token()

    @pytest.fixture
    def unique_username(self):
        """每次测试生成唯一用户名（时间戳）"""
        return f"auto_{int(time.time_ns())}"

    def test_add_user_success(self, token, unique_username):
        """TC-UM-ADD-001：新增用户成功，并验证数据库"""
        url = f"{BASE_URL}/system/user"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        data = {
            "userName": unique_username,
            "nickName": "自动化测试",
            "password": "Aa123456",
            "phonenumber": "13800138002",
            "status": "0"
        }
        resp = requests.post(url, headers=headers, json=data)
        # print("实际返回信息",resp.json())
        assert resp.status_code == 200
        assert resp.json().get("code") == 200

        # 🔥 数据库验证：确认数据真的落库了
        sql = f"SELECT user_name, nick_name FROM sys_user WHERE user_name = '{unique_username}'"
        db_result = query_db(sql)
        assert len(db_result) == 1, "数据库未查到新增用户"
        assert db_result[0][0] == unique_username, "数据库用户名不匹配"
        print(f"✅ 新增成功，数据库验证通过: {unique_username}")

    def test_add_user_duplicate(self, token):
        """TC-UM-ADD-014：重复用户名（预期失败）"""
        url = f"{BASE_URL}/system/user"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        data = {
            "userName": "admin",
            "nickName": "重复测试",
            "password": "Aa123456"
        }
        resp = requests.post(url, headers=headers, json=data)
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        assert "已存在" in resp.json().get("msg", "")
        print("✅ 重复拦截测试通过")

    def test_add_user_missing_nickname(self, token, unique_username):
        """TC-UM-ADD-010：昵称为空（预期失败）"""
        url = f"{BASE_URL}/system/user"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        data = {
            "userName": unique_username,
            "nickName": "",
            "password": "Aa123456"
        }
        resp = requests.post(url, headers=headers, json=data)
        assert resp.status_code == 200
        # 只要返回码不是 200 即认为拦截成功
        assert resp.json().get("code") != 200, "预期失败但实际成功"
        print(f"实际错误信息（供分析）：{resp.json().get('msg')}")
        print("✅ 空昵称拦截测试通过（后端返回数据库异常，建议优化提示）")