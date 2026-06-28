import requests


# ---------- 1. 登录函数（无需验证码，极简版） ----------
def login():
    """登录若依，直接返回 token"""
    url = "http://localhost:8080/login"
    payload = {
        "username": "admin",
        "password": "admin123"
    }
    resp = requests.post(url, json=payload)

    # 断言 HTTP 状态码为 200
    assert resp.status_code == 200, f"HTTP请求失败，状态码：{resp.status_code}"

    # 提取 token
    result = resp.json()
    token = result.get("token")
    if not token:
        print("登录失败，返回结果：", result)
        raise Exception("未获取到 token，请检查后端是否正常启动")

    print(f"✅ 登录成功，Token：{token[:20]}...")
    return token


# ---------- 2. 通用请求头 ----------
def get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }



# ---------- 3. 测试用例1：新增用户（正向） ----------
def test_add_user_success(token):
    print("\n▶ 执行测试用例：新增用户（正向）")
    url = "http://localhost:8080/system/user"
    headers = get_headers(token)
    data = {
        "userName": "test_final_001",
        "nickName": "最终测试",
        "password": "Aa123456",
        "phonenumber": "13800138001",
        "status": "0"
    }
    resp = requests.post(url, headers=headers, json=data)
    assert resp.status_code == 200, f"HTTP状态码异常：{resp.status_code}"
    assert resp.json().get("code") == 200, f"业务返回码异常：{resp.json()}"
    print("✅ 新增用户成功")


# ---------- 4. 测试用例2：重复创建（逆向） ----------
def test_add_user_duplicate(token):
    print("\n▶ 执行测试用例：用户名重复（预期失败）")
    url = "http://localhost:8080/system/user"
    headers = get_headers(token)
    data = {
        "userName": "admin",  # 已存在的用户名
        "nickName": "重复测试",
        "password": "Aa123456"
    }
    resp = requests.post(url, headers=headers, json=data)
    assert resp.status_code == 200
    assert resp.json().get("code") != 200, "预期失败但实际成功，可能用户名不存在"
    assert "登录账号已存在" in resp.json().get("msg", ""), "错误信息不符合预期"
    print("✅ 重复创建被正确拦截")


# ---------- 5. 测试用例3：昵称为空（逆向） ----------
def test_add_user_missing_nickname(token):
    print("\n▶ 执行测试用例：昵称为空（预期失败）")
    url = "http://localhost:8080/system/user"
    headers = get_headers(token)
    data = {
        "userName": "test_missing",
        "nickName": "",  # 昵称为空
        "password": "Aa123456"
    }
    resp = requests.post(url, headers=headers, json=data)
    assert resp.status_code == 200
    assert resp.json().get("code") != 200, "预期失败但实际成功"
    assert "nick_name" in resp.json().get("msg", ""), "错误信息未包含‘不能为空’字段提示"
    print("✅ 昵称为空被正确拦截")


# ---------- 6. 主执行入口 ----------
if __name__ == "__main__":
    try:
        # 先登录
        token = login()

        # 执行所有测试用例
        test_add_user_success(token)
        test_add_user_duplicate(token)
        test_add_user_missing_nickname(token)

        print("\n🎉 所有测试用例执行完毕！")
    except AssertionError as e:
        print(f"\n❌ 测试失败：{e}")
    except Exception as e:
        print(f"\n❌ 程序异常：{e}")