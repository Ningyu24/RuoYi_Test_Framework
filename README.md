---

```markdown
# 若依后台管理系统 – 测试实战项目（双版本演进）

本项目针对若依（RuoYi-Vue）后台管理系统的**用户管理模块**，从基础脚本逐步演进为分层自动化测试框架，完整覆盖了**手工测试 → 缺陷跟踪 → 接口自动化 → 数据库验证 → 性能测试 → 测试报告**的全流程测试实践。

> 📌 项目核心价值在于展示**从“能跑”到“能维护”的测试思维成长过程**。版本一完成功能验证，版本二实现工程化，两个版本均保留在仓库中，便于对比和学习。

---

## 🧪 项目概览

| 项目 | 说明 |
|------|------|
| 测试对象 | 若依管理系统（RuoYi-Vue v3.9.2）用户管理模块 |
| 测试类型 | 功能测试 / 接口自动化 / 性能测试 / 安全测试（XSS注入） |
| 测试周期 | 2026.06.25 – 2026.06.28 |
| 技术栈 | Python 3.9+ / Pytest / Requests / PyMySQL / Pytest-HTML |
| 产出物 | 22条手工用例 / 5个有效缺陷 / 3个自动化用例 / 性能测试报告 / 完整测试报告 |

---

## 📁 项目结构

```

RuoYi_Test_Framework/
├── README.md                    # 项目说明文档
├── performance_test.py          # 性能测试脚本（登录接口并发）
├── images/                      # 截图（测试报告、性能结果等）
│
├── v1-script/                   # 版本一：基础脚本（验证流程）
│   ├── test_user_management.py  # 裸跑脚本（函数式）
│   ├── test_user_pytest.py      # pytest格式脚本 + 数据库验证
│   ├── report.html              # pytest-html测试报告
│   ├── 【若依】用户管理模块测试用例.xlsx   # 22条手工用例
│   └── 测试点提取.xmind          # 测试思维导图
│
└── v2-framework/                # 版本二：分层测试框架（工程化）
├── common/                  # 公共层（HTTP封装、DB封装）
├── config/                  # 配置层（环境配置）
├── data/                    # 数据层（JSON数据驱动）
├── testcases/               # 测试用例层（pytest用例）
├── reports/                 # 测试报告输出目录
├── pytest.ini               # pytest配置文件
└── requirements.txt         # 项目依赖清单

```

---

## 🚀 快速开始

### 1. 环境要求
- Python 3.9+
- 若依后端服务（本地部署并启动）
- MySQL 8.0 / Redis
- 已关闭登录验证码（或已修改源码跳过校验）

### 2. 安装依赖

**版本一（v1-script）**：
```bash
cd v1-script
pip install -r requirements.txt   # 或手动安装 pytest, requests, pymysql, pytest-html
```

版本二（v2-framework）：

```bash
cd v2-framework
pip install -r requirements.txt
```

3. 配置数据库（版本二）

在 v2-framework/config/settings.py 中修改数据库连接信息：

```python
DB_PASSWORD = "你的MySQL密码"
```

4. 运行测试

版本一：

```bash
cd v1-script
pytest test_user_pytest.py --html=report.html --self-contained-html
```

版本二：

```bash
cd v2-framework
pytest testcases/ --html=reports/report.html --self-contained-html
```

5. 查看报告

在浏览器中打开生成的 report.html 或 reports/report.html 即可查看测试结果。

---

🧪 测试覆盖详情

手工测试用例（22条）

类型 数量 说明
正向用例 9条 正常新增、手机号、邮箱、部门、岗位、状态、备注、中英文混合、强密码
逆向用例 5条 昵称为空、昵称超长、用户名超短/超长、用户名重复
安全用例 1条 XSS注入测试（<script>标签）
其他 7条 查询、修改、删除、权限隔离等

自动化测试用例（3条）

用例编号 场景 预期结果 数据库验证
TC-UM-ADD-001 新增用户成功 code=200 ✅ 自动查表确认落库
TC-UM-ADD-014 重复用户名拦截 code≠200，提示“已存在” ❌ 无插入
TC-UM-ADD-010 昵称为空拦截 code≠200，提示“不能为空” ❌ 无插入

---

🐞 发现的缺陷

缺陷编号 标题 严重程度
BUG-001 输入 XSS 标签（abc<SCRIPT>）时系统静默过滤未提示用户 中等
BUG-002 删除超级管理员时提示“当前用户不能删除”，表述存在歧义 建议
BUG-003 昵称输入框超过30字后直接阻止输入，但无任何长度提示 一般
BUG-004 允许设置纯数字弱密码（如 123456），未校验密码复杂度 建议
BUG-005 昵称为空时后端抛出 SQL 异常，未返回业务友好提示 一般

---

⚡ 性能测试结果

测试场景 并发数 总请求数 成功率 平均响应时间 吞吐量
登录接口（常规负载） 10 20 100% 593ms 1.68 req/s
登录接口（高负载） 50 100 0% 5022ms 0.20 req/s

结论：在 10 并发下系统表现稳定；50 并发时出现性能瓶颈，推测为本地 Tomcat 线程池限制及登录逻辑耗时操作导致。

---

📊 测试结论

· 结论：有条件通过
· 依据：
  · 核心功能（增删改查）基本可用，未发现阻断性缺陷。
  · 存在 1 个中等严重度缺陷（XSS 过滤无提示）和 1 个一般缺陷（昵称为空 SQL 异常）。
· 建议：
  · 修复 BUG-001：增加前端输入提示，告知用户特殊字符被过滤。
  · 修复 BUG-005：在业务层增加昵称为空的校验，返回友好提示。
  · 增加密码复杂度校验（至少8位，含大小写字母和数字）。
  · 生产环境建议集群部署、Redis会话共享，优化高并发性能。

---

📦 技术栈

类别 技术
编程语言 Python 3.9+
测试框架 Pytest 7.x
HTTP客户端 Requests 2.x
数据库驱动 PyMySQL 1.x
报告生成 Pytest-HTML
版本控制 Git / GitHub

---

🤝 联系作者

· 作者：廖雪
· 邮箱：3399741447@qq.com
· GitHub：Ningyu24/RuoYi_Test_Framework

---

📌 版本说明

版本 状态 说明
v1-script ✅ 可用 基础脚本，验证流程通不通
v2-framework ✅ 可用 分层框架，可维护可扩展

两个版本均完整保留在仓库中，方便对比学习和迭代参考。

```

---

