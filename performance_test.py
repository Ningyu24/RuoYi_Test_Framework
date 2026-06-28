import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://localhost:8080"
THREAD_COUNT = 10   # 并发数（降低后可提高通过率）
REQUEST_COUNT = 20  # 总请求数

# ----------------- 登录获取 Token -----------------
def login_and_get_token():
    url = f"{BASE_URL}/login"
    payload = {"username": "admin", "password": "admin123"}
    resp = requests.post(url, json=payload, timeout=5)
    if resp.status_code == 200:
        token = resp.json().get("token")
        if token:
            return token
    raise Exception("登录失败，无法获取 Token")

# ----------------- 单次登录请求（性能测试目标） -----------------
def single_login():
    start = time.time()
    try:
        resp = requests.post(f"{BASE_URL}/login", json={"username": "admin", "password": "admin123"}, timeout=5)
        if resp.status_code == 200 and resp.json().get("token"):
            return time.time() - start, True
        else:
            return time.time() - start, False
    except requests.exceptions.RequestException:
        return time.time() - start, False

# ----------------- 并发执行 -----------------
def run_performance():
    print(f"开始性能测试：{THREAD_COUNT} 并发，共 {REQUEST_COUNT} 次请求")
    times = []
    success = 0
    failure = 0

    with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
        futures = [executor.submit(single_login) for _ in range(REQUEST_COUNT)]
        for future in as_completed(futures):
            duration, ok = future.result()
            times.append(duration)
            if ok:
                success += 1
            else:
                failure += 1

    if not times:
        print("没有请求完成，请检查网络或后端状态")
        return

    avg_time = sum(times) / len(times) * 1000
    min_time = min(times) * 1000
    max_time = max(times) * 1000

    print(f"\n--- 性能结果 ---")
    print(f"总请求数：{REQUEST_COUNT}")
    print(f"成功：{success}，失败：{failure}")
    print(f"平均响应时间：{avg_time:.2f} ms")
    print(f"最小响应时间：{min_time:.2f} ms")
    print(f"最大响应时间：{max_time:.2f} ms")
    print(f"吞吐量：{REQUEST_COUNT / sum(times):.2f} req/s")

if __name__ == "__main__":
    run_performance()