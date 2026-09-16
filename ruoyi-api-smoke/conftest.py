import pytest
import requests
import allure 
import json
import platform


from pathlib import Path
from config.config import *
from libs.global_data import datas
from libs.login import login
from libs.login_by_case_id import login_by_case_id


def get_admin_headers():
    """每次请求时读取当前最新的管理员 token。"""

    token = datas.get("TOKEN")

    assert token, "全局变量 datas 中没有管理员 TOKEN"

    return {
        "Authorization": f"Bearer {token}"
    }
    


'''
admin_token             session   管理员整个测试会话登录一次
prepared_user      session   整个测试会话创建一次前置用户，创建测试用户，并保证清理时用户先于角色删除
prepared_role      session   整个测试会话创建一次前置角色

user_token        function  每条需要普通用户身份的测试重新登录
'''
    
def pytest_make_parametrize_id(
    config,
    val,
    argname
):
    """
    将参数化测试名称 case0、case1
    替换为 Excel 中的用例编号。
    """

    if (
        argname == "case"
        and isinstance(val, dict)
    ):
        return val.get("id")

    return None
# ==================================================
# 管理员 Token
# SMK-LOGIN-001
# 整个 pytest 会话只登录一次
# ==================================================
@pytest.fixture(scope="session")
def admin_token():

    token = login_by_case_id(
        "SMK-LOGIN-001"
    )

    assert token, (
        "管理员登录成功用例未返回 token"
    )

    # 初始化全局管理员 token
    datas["TOKEN"] = token

    yield

    datas.pop("TOKEN", None)

# =================================================
# 普通用户 Token
# SMK-LOGIN-002
# 每条测试重新登录一次
# 避免角色/权限发生变化后继续使用旧 token
# ==================================================
@pytest.fixture(scope="function")
def user_token(prepared_user):

    login_response = login(
        prepared_user["username"],
        prepared_user["password"]
    )

    assert login_response.status_code == 200

    login_result = login_response.json()

    assert login_result.get("code") == 200, (
        f"普通用户登录失败：{login_result}"
    )

    normal_user_token = login_result.get("token")

    assert normal_user_token, (
        "普通用户登录成功但未返回 token"
    )

    datas["USER_TOKEN"] = normal_user_token

    yield normal_user_token

    datas.pop("USER_TOKEN", None)
# =================================================
# 创建所需用户
# =================================================

@pytest.fixture(scope="session")
def prepared_user(admin_token, prepared_role):

        # 0. 清理上一次测试残留用户
        response = requests.get(
        BASE_URL + USER_LIST_URL,
        headers=get_admin_headers(),
        params={
            "userName": USER_NAME
        }
    )

        result = response.json()

        assert result["code"] == 200, (
            f"查询历史测试用户失败：{result}"
        )
        old_user = next(
            (
                row for row in result["rows"]
                if row.get("userName") == USER_NAME
            ),
            None
        )

        if old_user:
            old_user_id = old_user["userId"]

            delete_response = requests.delete(
                BASE_URL + USER_URL + f"/{old_user_id}",
                headers=get_admin_headers()
            )

            delete_result = delete_response.json()

            assert delete_result["code"] == 200, (
                f"清理历史测试用户失败：{delete_result}"
            )

            print(
                f"\n[数据准备] 已清理历史测试用户："
                f"{USER_NAME}，USER_ID={old_user_id}"
            )

        # 1. 创建用户
        create_data = {
            "userName": USER_NAME,
            "nickName": NICK_NAME,
            "password": PASSWORD,
            "status": "0",
            "deptId": 103,
            "postIds": [],
            "roleIds": []
        }

        response = requests.post(
            BASE_URL + USER_URL,
            headers=get_admin_headers(),
            json=create_data
        )

        result = response.json()

        assert result["code"] == 200, (
            f"创建测试用户失败：{result}"
        )

        # 2. 查询用户，获取 USER_ID
        response = requests.get(
            BASE_URL + USER_LIST_URL,
            headers=get_admin_headers(),
            params={
                "userName": USER_NAME
            }
        )

        result = response.json()

        assert result["code"] == 200, (
        f"查询测试用户失败：{result}"
    )
        assert result["rows"], (
        "创建用户后未查询到测试用户"
    )
        user = next(
            (
                row for row in result["rows"]
                if row.get("userName") == USER_NAME
            ),
            None
        )

        assert user, (
            f"创建用户后未精确查询到测试用户：{USER_NAME}"
        )

        user_id = user["userId"]

        # 保存动态数据
        datas["USER_ID"] = user_id
        datas["USER_NAME"] = USER_NAME
        datas["USER_PASSWORD"] = PASSWORD
        datas["NICK_NAME"] = NICK_NAME
        datas["UPDATED_NICK_NAME"] = UPDATED_NICK_NAME

        # 3. 返回测试数据，为后续用例提供测试数据
        yield {
            "user_id": user_id,
            "username": USER_NAME,
            "password": PASSWORD
        }

        # 4. teardown 清理
        response = requests.delete(
            BASE_URL + USER_URL + f"/{user_id}",
            headers=get_admin_headers()
        )

        result = response.json()

        if result.get("code") == 200:
            print(
                f"\n[数据清理] 测试用户删除成功："
                f"{USER_NAME}，USER_ID={user_id}"
            )
        else:
            print(
                f"\n[数据清理] 测试用户删除失败：{result}"
            )

        datas.pop("USER_ID", None)
        datas.pop("USER_NAME", None)
        datas.pop("USER_PASSWORD", None)
        datas.pop("NICK_NAME", None)
        datas.pop("UPDATED_NICK_NAME", None)


# ==================================================
# 创建所需角色
# ==================================================           
@pytest.fixture(scope="session")
def prepared_role(admin_token):

    # ==================================================
    # 0. 清理上一次测试残留角色
    # ==================================================

    response = requests.get(
        BASE_URL + ROLE_LIST_URL,
        headers=get_admin_headers(),
        params={
            "roleName": ROLE_NAME
        }
    )

    result = response.json()

    assert result["code"] == 200, (
        f"查询历史测试角色失败：{result}"
    )

    old_role = next(
        (
            row for row in result["rows"]
            if row.get("roleName") == ROLE_NAME
        ),
        None
    )

    if old_role:
        old_role_id = old_role["roleId"]

        delete_response = requests.delete(
            BASE_URL + ROLE_URL + f"/{old_role_id}",
            headers=get_admin_headers()
        )

        delete_result = delete_response.json()

        assert delete_result["code"] == 200, (
            f"清理历史测试角色失败：{delete_result}"
        )
        
        print(
            f"\n[数据准备] 已清理历史测试角色："
            f"{ROLE_NAME}，ROLE_ID={old_role_id}"
        )

    # 1. 创建角色
    create_data = {
        "roleName": ROLE_NAME,
        "roleKey": ROLE_KEY,
        "roleSort": 1,
        "status": "0",
        "menuIds": [1, 100, 1001],
        "deptIds": [],
        "menuCheckStrictly": True,
        "deptCheckStrictly": True
    }

    response = requests.post(
        BASE_URL + ROLE_URL,
        headers=get_admin_headers(),
        json=create_data
    )

    result = response.json()

    assert result["code"] == 200, (
        f"创建测试角色失败：{result}"
    )

    # 2. 查询角色，拿 ROLE_ID
    response = requests.get(
        BASE_URL + ROLE_LIST_URL,
        headers=get_admin_headers(),
        params={
            "roleName": ROLE_NAME
        }
    )

    result = response.json()

    assert result["code"] == 200, (
        f"查询测试角色失败：{result}"
    )

    assert result["rows"], (
        "创建角色后未查询到测试角色"
    )

    role = next(
        (
            row for row in result["rows"]
            if row.get("roleName") == ROLE_NAME
        ),
        None
    )

    assert role, (
        f"创建角色后未精确查询到测试角色：{ROLE_NAME}"
    )

    role_id = role["roleId"]

    # ==================================================
    # 3. 保存动态数据
    # ==================================================
    datas["ROLE_ID"] = role_id
    datas["ROLE_NAME"] = ROLE_NAME
    datas["ROLE_KEY"] = ROLE_KEY
        
    print(
        f"\n[数据准备] 测试角色创建成功："
        f"{ROLE_NAME}，ROLE_ID={role_id}"
    )


    # ==================================================
    # 4. 提供测试数据
    # ==================================================

    yield {
        "role_id": role_id,
        "role_name": ROLE_NAME,
        "role_key": ROLE_KEY
    }

    # ==================================================
    # 5. teardown 清理
    # ==================================================

    response = requests.delete(
        BASE_URL + ROLE_URL + f"/{role_id}",
        headers=get_admin_headers()
    )

    result = response.json()

    if result.get("code") == 200:
        print(
            f"\n[数据清理] 测试角色删除成功："
            f"{ROLE_NAME}，ROLE_ID={role_id}"
        )
    else:
        print(
            f"\n[数据清理] 测试角色删除失败：{result}"
        )

    datas.pop("ROLE_ID", None)
    datas.pop("ROLE_NAME", None)
    datas.pop("ROLE_KEY", None)


@pytest.fixture(autouse=True)
def set_allure_case_info(request):
    """
    自动设置 Allure 分类，
    并显示当前 Excel 用例数据。
    """

    callspec = getattr(
        request.node,
        "callspec",
        None
    )

    if callspec is None:
        return

    case = callspec.params.get("case")

    if not isinstance(case, dict):
        return
    # ==============================
    # 设置 Allure 分类和用例标题
    # ==============================
    feature = (
        case.get("feature")
        or "未分类"
    )

    story = (
        case.get("story")
        or "未分类"
    )

    # 按 feature 分类
    allure.dynamic.feature(feature)

    # feature 下面继续按 story 分类
    allure.dynamic.story(story)

    # 用例名称显示：ID + title
    allure.dynamic.title(
        f"ID:{case['id']} ----- "
        f"{case['title']}"
    )


    # 如果之前增加过 Suites 分类，保留
    allure.dynamic.parent_suite(
        "若依接口自动化测试"
    )

    allure.dynamic.suite(feature)

    # ==============================
    # 2. 缩短 Parameters 中的 case
    # ==============================
    allure.dynamic.parameter(
        "case",
        case.get("id")
    )

def pytest_sessionfinish(
    session,
    exitstatus
):
    """
    测试结束后生成 Allure 环境信息。
    """

    results_dir = (
        session.config.getoption(
            "allure_report_dir",
            default=None
        )
    )

    # 没有使用 --alluredir 时不生成
    if not results_dir:
        return

    results_path = Path(
        results_dir
    )

    results_path.mkdir(
        parents=True,
        exist_ok=True
    )

    environment_content = "\n".join(
        [
            "Environment=Local",
            f"Base_URL={BASE_URL}",
            f"Python={platform.python_version()}",
            f"Pytest={pytest.__version__}",
            "Framework=pytest",
            "Project=RuoYi API Smoke",
        ]
    )

    environment_file = (
        results_path
        / "environment.properties"
    )

    environment_file.write_text(
        environment_content,
        encoding="utf-8"
    )