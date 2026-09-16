import pytest
import requests

from config.config import BASE_URL
from libs.redis_utils import get_captcha_code
from libs.excel_utils import read_excel


def login_by_case_id(case_id):
    """
    根据 auth sheet 中的 case_id 执行登录。

    支持：
    SMK-LOGIN-001：管理员登录成功
    SMK-LOGIN-002：普通用户登录成功
    SMK-LOGIN-003：已停用用户登录失败

    返回：
    - 登录成功：返回 token
    - 登录失败：返回 None
    """

    # ==============================
    # 1. 读取 auth sheet
    # ==============================
    data = read_excel(
        sheet_name="auth"
    )

    login_case = None

    for case in data:
        if case["id"] == case_id:
            login_case = case
            break

    assert login_case is not None, (
        f"Excel 中没有找到登录用例：{case_id}"
    )

    # ==============================
    # 2. 获取验证码接口
    # ==============================
    captcha_response = requests.get(
        f"{BASE_URL}/captchaImage"
    )

    assert captcha_response.status_code == 200, (
        f"获取验证码 HTTP 状态码异常："
        f"{captcha_response.status_code}"
    )

    captcha_data = captcha_response.json()

    assert captcha_data.get("code") == 200, (
        f"获取验证码业务失败：{captcha_data}"
    )

    uuid = captcha_data.get("uuid")

    assert uuid, (
        "获取验证码成功，但响应中没有 uuid"
    )

    # ==============================
    # 3. 从 Redis 获取验证码
    # ==============================
    captcha_code = get_captcha_code(
        uuid
    )

    assert captcha_code, (
        f"Redis 中没有获取到验证码，uuid={uuid}"
    )

    # ==============================
    # 4. 读取 Excel 登录请求体
    # ==============================
    assert login_case.get("json"), (
        f"{case_id} 的 json 请求体为空"
    )

    login_data = eval(
        login_case["json"]
    )

    # 动态补充验证码
    login_data["code"] = captcha_code
    login_data["uuid"] = uuid

    # ==============================
    # 5. 发送登录请求
    # ==============================
    response = requests.post(
        f"{BASE_URL}{login_case['path']}",
        json=login_data
    )

    result = response.json()

    # ==============================
    # 6. HTTP 状态码断言
    # ==============================
    assert response.status_code == int(
        login_case["statusCode"]
    ), (
        f"{case_id} HTTP 状态码断言失败："
        f"预期={login_case['statusCode']}，"
        f"实际={response.status_code}"
    )

    # ==============================
    # 7. 业务响应断言
    # ==============================
    check_res_body = eval(
        login_case["check_res_body"]
    )

    for key, expected_value in check_res_body.items():

        assert key in result, (
            f"{case_id} 响应中缺少字段：{key}"
        )

        actual_value = result[key]

        assert actual_value == expected_value, (
            f"{case_id} {key} 断言失败："
            f"预期={expected_value}，"
            f"实际={actual_value}"
        )

    # ==============================
    # 8. 打印登录执行结果
    # ==============================
    print(
        "\n========== 登录接口执行结果 =========="
    )

    print(
        f"用例ID：{case_id}"
    )

    print(
        f"用例：{login_case['title']}"
    )

    print(
        f"账号：{login_data.get('username')}"
    )

    print(
        f"密码：{login_data.get('password')}"
    )

    print(
        f"HTTP状态码：{response.status_code}"
    )

    print(
        f"业务响应："
        f"code={result.get('code')}, "
        f"msg={result.get('msg')}"
    )

    # ==============================
    # 9. 成功登录 / 失败登录区分
    # ==============================
    token_value = result.get("token")

    if token_value:

        print(
            "TOKEN：提取成功"
        )

    else:

        print(
            "TOKEN：未返回"
        )

    print(
        "======================================\n"
    )

    # ==============================
    # 10. 返回 token
    # ==============================
    return token_value