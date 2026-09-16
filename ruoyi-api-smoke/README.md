# cases

## test_auth.py-->登录链路
覆盖验证码以及登录接口：
- GET /captchaImage-->包含获取验证码，提取uuid，Python 根据 uuid 查询 Redis,拿到验证码答案'code'
- POST /login-->拿着验证码接口抓到的uuid和code登录-->提取 token

### 数据驱动sheet-->autu
- **SMK-LOGIN-001必须为登陆成功用例**，夹具需做前置处理，从该用例提取token
- conftest中根据自己的excel数据sheet名称更改读取的sheet_name，目前默认sheet_name="auth"

## test_user.py-->用户管理
- 必须先执行登录，再执行用户查询-->获取动态data（ruoyi-api-smoke\libs\global_data.py），否则无法直接获取Authorization: Bearer 

## test_role.py-->简单角色管理
- 主要负责CRUD + 二次断言

## test_permission_flow.py--> 复杂角色管理中：用户--角色状态关联问题
- 专门负责较复杂业务流程 / 状态迁移测试

# config
## config
- 开始测试前需要根据个人情况配置环境设置和测试数据路径配置
- 其余所需配置可在此文件按需补充



建议按这个顺序完整阅读：
1. 第 6～10 节：掌握项目主线
   - 动态变量和接口关联
   - fixture 生命周期
   - 响应断言
   - 登录与 Token
   - permission 权限业务链
2. 第 12 节：理解真实排错经历
   - USER_ID 提取失败
   - 上游失败引发连锁报错
   - 已删除用户产生脏关联
   - 新旧 Token 混用
   - fixture 批量报错
3. 第 16～18 节：准备面试
   - 项目介绍
   - 简历表述
   - 五个真实案例
   - 高频追问
4. 第 1～5 节：补齐项目背景和基础
   - 项目规模与定位
   - 从功能测试转成接口测试
   - 目录结构
   - HTTP、Requests
   - Excel 数据驱动
5. 第 11 节：单独复习 Allure
   - 报告生成原理
   - feature、story、title
   - step 和 attach
   - 请求响应附件
   - 数据脱敏
6. 第 13～14 节：练习实际运行和排错
   - 自己敲一遍运行命令
   - 练习判断收集错误、setup error、接口失败和断言失败
   - 熟悉从第一条失败向上游排查的方法
7. 第 15 节：准备“项目还有什么不足”
   - 数据权限验证不够完整
   - 权限列表没有完全替代真实接口鉴权验证
   - 脱敏、依赖锁定和失败清理仍可改善
8. 最后看第 19 节
   - 核对代码来源
   - 了解哪些是旧结论
   - 避免面试时把“讨论过的能力”说成“已经实现的能力”