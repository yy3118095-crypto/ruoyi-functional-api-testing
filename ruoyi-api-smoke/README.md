# RuoYi API Smoke

基于 `pytest + requests + Excel + Redis + Allure` 的若依接口冒烟测试项目。

当前覆盖登录、用户管理、角色管理，以及用户与角色状态关联等业务流程。测试数据由 Excel 驱动，运行期间产生的用户、角色和 Token 等动态数据统一保存在 `libs/global_data.py` 中。

# 项目结构

```text
ruoyi-api-smoke/
├─ cases/                     # 测试用例
│  ├─ test_auth.py            # 验证码及登录链路
│  ├─ test_user.py            # 用户管理
│  ├─ test_role.py            # 角色管理
│  └─ test_permission_flow.py # 用户、角色及 Token 状态流转
├─ config/
│  └─ config.py               # 环境、接口路径及测试数据配置
├─ data/
│  └─ datas.xlsx              # Excel 数据驱动文件
├─ libs/                      # 请求、断言、提取、登录等公共方法
├─ conftest.py                # 公共夹具及 Allure 配置
├─ pytest.ini                 # pytest 配置
└─ requirements.txt           # Python 依赖
```

# 环境准备

## 1. 基础环境

- Python 3.10 及以上版本
- 可正常访问的若依后端服务
- Redis 服务，且测试机可以读取验证码数据
- Allure Commandline（仅生成并查看 Allure 报告时需要）

## 2. 安装依赖

建议在项目根目录创建虚拟环境后安装依赖：

```bash
python -m venv .venv
```

Windows PowerShell 激活虚拟环境：

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## 3. 修改配置

开始测试前，根据本地环境修改 `config/config.py`：

- `BASE_URL`：若依后端地址，目前默认为 `http://localhost/dev-api`
- `ADMIN_USERNAME`、`ADMIN_PASSWORD`：管理员账号和密码
- `PATH`：Excel 测试数据路径，目前默认为 `data/datas.xlsx`
- `SHEET_NAME`：默认读取的 sheet，目前为 `auth`
- `USER_*`：测试用户相关数据
- `ROLE_*`：测试角色相关数据

验证码通过 `libs/redis_utils.py` 查询 Redis，目前默认配置为：

```text
host=localhost
port=6379
db=0
key=captcha_codes:{uuid}
```

Redis 配置或验证码 key 规则不一致时，需要同步修改该文件。

# Excel 数据驱动

测试数据文件：`data/datas.xlsx`

当前用例对应的 sheet：

- `auth` --> 登录接口
- `user` --> 用户管理接口
- `role` --> 角色管理接口
- `permission` --> 权限及状态流转

Excel 第 3 行为字段名，从第 4 行开始读取测试数据；只有 `is_true` 为真值的用例才会参与执行。

常用字段说明：

- `id` --> 用例编号，也是 pytest 参数化用例名称
- `title` --> 用例标题
- `feature`、`story` --> Allure 报告分类
- `method`、`url` --> 请求方式和接口地址
- `headers`、`params`、`data`、`json` --> 请求数据
- `statusCode` --> 预期 HTTP 状态码
- `check_res_body` --> 响应体断言
- `jsonExData` --> 动态数据提取规则
- `action` --> 二次业务校验或状态流转动作
- `is_true` --> 是否执行该条用例

Excel 中可以使用 `{{TOKEN}}`、`{{USER_ID}}`、`{{ROLE_ID}}`、`{{USER_TOKEN}}` 等变量。执行时会从 `libs/global_data.py` 的 `datas` 中替换为当前动态值。

# cases

## test_auth.py --> 登录链路

覆盖验证码以及登录接口：

- `GET /captchaImage` --> 获取验证码并提取 `uuid`，再根据 `uuid` 从 Redis 查询验证码答案 `code`
- `POST /login` --> 携带 `uuid` 和 `code` 登录，登录成功后提取 Token

### 数据驱动 sheet --> auth

- **`SMK-LOGIN-001` 必须为管理员登录成功用例**，`admin_token` 夹具会从该用例提取 Token
- `test_auth.py` 当前暂不执行 `SMK-LOGIN-008` 至 `SMK-LOGIN-011`
- 修改 sheet 名称时，需要同步检查 `config/config.py` 和对应测试文件中的 `read_excel(sheet_name=...)`

## test_user.py --> 用户管理

- 覆盖用户查询、新增、修改和删除等接口
- 必须先完成管理员登录，再执行用户管理用例，否则无法得到 `Authorization: Bearer <TOKEN>`
- 修改用户后会重新查询目标用户，对昵称等业务结果进行二次断言
- 动态数据保存在 `libs/global_data.py`，可供后续用例继续使用

## test_role.py --> 简单角色管理

- 主要负责角色 CRUD、响应断言和动态数据提取
- `action` 字段用于区分 `list`、`add`、`update`、`delete` 等操作

## test_permission_flow.py --> 复杂权限流程

专门负责较复杂的业务流程和状态迁移测试，包括：

- 普通用户停用后无法登录
- 普通用户恢复后可以重新登录
- 用户删除后无法登录
- 管理员退出后旧 Token 失效
- 管理员重新登录后新 Token 有效

该文件中的用例存在前后状态依赖，建议按 Excel 中的既定顺序整体执行，不要随意单独运行中间步骤。

# 公共夹具

`conftest.py` 中的主要夹具：

- `admin_token`（session）--> 整个测试会话登录一次管理员，并保存 `TOKEN`
- `prepared_role`（session）--> 创建测试角色，结束后自动删除
- `prepared_user`（session）--> 创建测试用户，结束后自动删除
- `user_token`（function）--> 每条需要普通用户身份的测试重新登录，避免继续使用权限变化前的旧 Token

执行前会尝试清理同名历史测试数据；执行完成后也会自动清理本次创建的用户和角色。建议为 `USER_NAME`、`ROLE_NAME` 配置专用测试名称，避免与人工维护的数据重名。

# 运行测试

以下命令均在项目根目录执行。

## 运行全部用例

```bash
python -m pytest -s -v cases
```

## 运行某个测试文件

不输出 `print` 信息：

```bash
python -m pytest cases/test_auth.py
```

输出 `print` 信息：

```bash
python -m pytest -s cases/test_auth.py
```

## 运行一组测试文件

```bash
python -m pytest -s cases/test_user.py cases/test_role.py
```

## 运行某条用例

参数化用例 ID 会使用 Excel 中的 `id`，可通过 `-k` 筛选：

```bash
python -m pytest -s cases/test_auth.py -k "SMK-LOGIN-001"
```

# Allure 报告

生成 Allure 测试结果：

```bash
python -m pytest cases -s -v --alluredir=./report/allure-results --clean-alluredir
```

打开报告：

```bash
allure serve ./report/allure-results
```

报告会按 Excel 中的 `feature`、`story` 分类，并自动写入当前运行环境、`BASE_URL`、Python 和 pytest 版本等信息。

# 注意事项

- 运行登录用例前，确认若依后端与 Redis 均已启动
- 测试机必须能直接读取若依验证码所在的 Redis 数据库
- `SMK-LOGIN-001` 必须保持为有效的管理员登录成功用例
- 权限流程包含严格的状态依赖，建议单进程、按既定顺序执行
- 不建议直接启用 `pytest-xdist` 并行执行，多个用例会共享 `libs/global_data.py` 中的动态数据
- 用例异常中断时可能来不及执行 teardown；下次运行会清理同名历史用户和角色
- Excel 中的字典、列表等字段需要保持合法的 Python 字面量格式，否则 `ast.literal_eval` 会解析失败

# 常见问题

## Redis 中未获取到验证码

检查 Redis 地址、端口、数据库编号及 key 前缀，并确认后端验证码功能已开启。

## 全局变量 datas 中没有管理员 TOKEN

检查 `SMK-LOGIN-001` 是否启用且能够登录成功，并确认管理员账号、密码和 Excel 登录数据一致。

## Excel sheet 不存在或用例未读取

检查 sheet 名称是否与测试文件中的 `read_excel(sheet_name=...)` 一致；同时确认第 3 行是字段名，且目标用例的 `is_true` 已启用。

## 接口返回 401 或 Token 无效

确认请求头使用 `Authorization: Bearer <TOKEN>`，并检查该用例依赖的登录或刷新 Token 步骤是否已经执行。
