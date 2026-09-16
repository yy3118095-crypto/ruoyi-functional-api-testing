#环境配置-->utils\excel_to_dict.py
# ==============================
#基础环境配置
# ==============================
BASE_URL = "http://localhost/dev-api"

# ==============================
#API接口路径
# ==============================
# - ♥认证
LOGIN_URL = "/login"
CAPTCHA_URL = "/captchaImage"
    
# - ♥用户管理
USER_URL = "/system/user"
USER_LIST_URL = "/system/user/list"
USER_UNUSED = "/system/user/changeStatus"

# - ♥角色管理
ROLE_URL = "/system/role"
ROLE_LIST_URL = "/system/role/list"

# ==============================
# 管理员账号
# ==============================
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# ==============================
#测试数据路径配置 -->utils\excel_utils.py
# ==============================
PATH = 'data/datas.xlsx'
SHEET_NAME = 'auth'
#创建用户
USER_NAME = 'test_smoke_user_001'
NICK_NAME = 'test_smoke_user_001'
PASSWORD = '123456'
UPDATED_NICK_NAME = 'test_smoke_user_updated'
#创建角色
ROLE_NAME = 'test_smoke_role_001'
ROLE_KEY = 'test_smoke_role_001'

