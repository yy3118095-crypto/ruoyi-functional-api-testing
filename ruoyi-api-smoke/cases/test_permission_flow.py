import requests
import pytest
import ast
import allure

from jinja2 import StrictUndefined, Template
from libs.allure_request import (
    parse_response
)
from libs.global_data import datas
from libs.excel_utils import read_excel
from libs.excel_to_dict import excel_to_dict
from libs.extract_utils import extract_data
from libs.assert_response import assert_response
from libs.login import login

from config.config import *


class Test_permission_flow:

    # 读取 permission sheet
    data = read_excel(
        sheet_name="permission"
    )

    # ==============================
    # 验证账号能够正常登录并返回 token
    # ==============================
    def _login_success(
        self,
        username,
        password
    ):
        response = login(
            username,
            password
        )

        assert response.status_code == 200, (
            f"登录 HTTP 状态码异常："
            f"{response.status_code}"
        )

        result = response.json()

        assert result.get("code") == 200, (
            f"预期登录成功，实际响应："
            f"{result}"
        )

        token = result.get("token")

        assert token, (
            f"登录成功但没有返回 token："
            f"{result}"
        )

        return token

    # ==============================
    # 验证账号登录失败、错误提示符合预期且没有返回 token
    # ==============================
    def _assert_login_failure(
        self,
        username,
        password,
        expected_message
    ):
        response = login(
            username,
            password
        )

        assert response.status_code == 200, (
            f"登录 HTTP 状态码异常："
            f"{response.status_code}"
        )

        result = response.json()

        assert result.get("code") == 500, (
            f"预期登录失败，实际响应："
            f"{result}"
        )

        assert (
            result.get("msg")
            == expected_message
        ), (
            f"登录失败提示错误："
            f"预期={expected_message}，"
            f"实际={result.get('msg')}"
        )

        assert not result.get("token"), (
            f"预期登录失败，但仍返回 token："
            f"{result}"
        )

    # ==============================
    # permission 数据驱动
    # ==============================
    @pytest.mark.parametrize(
        "case",
        data
    )
    def test_permission_api(
        self,
        case,
        admin_token,
        prepared_user,
        prepared_role
    ):
        username = prepared_user[
            "username"
        ]

        password = prepared_user[
            "password"
        ]

        action = case.get("action")
    

        # ==============================
        # 3. 退出后重新获取管理员 token
        # 必须在替换 Excel 变量前执行
        # ==============================
        if action == "verify_new_token":
            datas["TOKEN"] = (
                self._login_success(
                    ADMIN_USERNAME,
                    ADMIN_PASSWORD
                )
            )
            
        if action == "refresh_user_token":
            datas["USER_TOKEN"] = self._login_success(
                username,
                password
            )

        # ==============================
        # 4. 替换 Excel 动态变量
        # ==============================
        case = ast.literal_eval(
            Template(
                str(case),
                undefined=StrictUndefined
            ).render(datas)
        )

        # ==============================
        # 5. Excel 转 requests 参数
        # ==============================
        request_data, check_res_body = (
            excel_to_dict(case)
        )

        # ==============================
        # 6. 退出前保存旧 token
        # ==============================
        if action == "logout_admin":
            datas["OLD_TOKEN"] = (
                datas["TOKEN"]
            )

        # ==============================
        # 7. 发送 Excel 接口请求
        # ==============================
        response = requests.request(
            **request_data
        )

        result = parse_response(
            response
        )

        # ==============================
        # 8. HTTP 状态码断言
        # ==============================
        assert response.status_code == int(
            case["statusCode"]
        ), (
            f"{case['id']} HTTP状态码错误："
            f"预期={case['statusCode']}，"
            f"实际={response.status_code}"
        )

        # ==============================
        # 9. Excel 响应内容断言
        # ==============================
        assert_response(
            result,
            check_res_body
        )

        # ==============================
        # 10. 动态数据提取
        # ==============================
        extract_data(
            case,
            request_data,
            result,
            datas
        )

        # ==============================
        # 11. 停用后登录失败
        # ==============================
        if action == "disable_user":

            self._assert_login_failure(
                username,
                password,
                "用户已封禁，请联系管理员"
            )

            print(
                "[二次校验] "
                "用户停用后登录失败"
            )

        # ==============================
        # 12. 恢复后登录成功
        # ==============================
        elif action == "enable_user":

            datas["USER_TOKEN"] = (
                self._login_success(
                    username,
                    password
                )
            )

            print(
                "[二次校验] "
                "用户恢复后登录成功"
            )

        # ==============================
        # 13. 删除后登录失败
        # ==============================
        elif action == "delete_user":

            self._assert_login_failure(
                username,
                password,
                "用户不存在/密码错误"
            )

            print(
                "[二次校验] "
                "用户删除后登录失败"
            )

        # ==============================
        # 14. 管理员退出
        # ==============================
        elif action == "logout_admin":

            print(
                "[二次校验] "
                "管理员退出成功，"
                "已保存 OLD_TOKEN"
            )

        # ==============================
        # 15. 旧 token 失效
        # Excel 已负责响应断言
        # ==============================
        elif action == "verify_old_token":

            print(
                "[二次校验] "
                "退出后的 OLD_TOKEN 已失效"
            )

        # ==============================
        # 16. 新 token 有效
        # Excel 已负责查询成功断言
        # ==============================
        elif action == "verify_new_token":

            print(
                "[二次校验] "
                "管理员重新登录后的新 TOKEN 有效"
            )

        print(
            f"【{case['id']}】执行成功："
            f"{case['title']}"
        )
