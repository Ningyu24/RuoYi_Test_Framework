# testcases/test_user_api.py
import pytest
from common.http_client import HttpClient
from common.db_client import DbClient
import json
from pathlib import Path

def load_test_data():
    # 获取当前文件所在目录的父目录（即项目根目录）
    base_dir = Path(__file__).resolve().parent.parent
    file_path = base_dir / "data" / "user_data.json"
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

class TestUserAPI:
    def test_add_user_success(self, api_client, unique_username, db_client):
        """新增用户成功，并验证数据库"""
        data = {
            "userName": unique_username,
            "nickName": "自动化",
            "password": "Aa123456",
            "phonenumber": "13800138002",
            "status": "0"
        }
        resp = api_client.post("/system/user", json=data)
        assert resp.status_code == 200
        assert resp.json().get("code") == 200

        # 数据库验证
        sql = f"SELECT user_name FROM sys_user WHERE user_name = '{unique_username}'"
        result = db_client.query_one(sql)
        assert result is not None
        assert result[0] == unique_username
        print(f"✅ 新增成功，数据库验证通过: {unique_username}")

    def test_add_user_duplicate(self, api_client):
        """重复用户名（预期失败）"""
        data = {
            "userName": "admin",
            "nickName": "重复测试",
            "password": "Aa123456"
        }
        resp = api_client.post("/system/user", json=data)
        assert resp.status_code == 200
        assert resp.json().get("code") != 200
        assert "已存在" in resp.json().get("msg", "")
        print("✅ 重复拦截测试通过")

    def test_add_user_missing_nickname(self, api_client, unique_username):
        """昵称为空（预期失败）"""
        data = {
            "userName": unique_username,
            "nickName": "",
            "password": "Aa123456"
        }
        resp = api_client.post("/system/user", data=data)
        assert resp.status_code == 200
        # 只要返回码不是 200 即认为拦截成功
        assert resp.json().get("code") != 200, "预期失败但实际成功"
        print(f"实际错误信息（供分析）：{resp.json().get('msg')}")
        print("✅ 空昵称拦截测试通过（后端返回数据库异常，建议优化提示）")

    @pytest.mark.parametrize("test_data", [
        load_test_data()["valid_user"],
        load_test_data()["invalid_user"]
    ])
    def test_add_user_data_driven(self, api_client,unique_username, test_data):
        """数据驱动测试：从JSON读取数据"""
        data = {
            "userName": unique_username,
            **test_data  # 将JSON中的数据展开
        }
        resp = api_client.post("/system/user", json=data)
        # 根据不同数据预期不同结果，这里简化演示
        assert resp.status_code == 200
        if test_data.get("nickName") == "":
            assert resp.json().get("code") != 200
        else:
            assert resp.json().get("code") == 200