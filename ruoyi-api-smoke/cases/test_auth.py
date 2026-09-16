import requests
import pytest
import ast
import allure
from libs.allure_request import (
    execute_request
)
from libs.excel_utils import read_excel
from config.config import *
from libs.redis_utils import get_captcha_code

#登录接口
class Test_login:#这里用读取excel的形式进行数据驱动
    #读测试数据
    data = read_excel(sheet_name="auth")

    # 暂时不执行第 8~11 条用例
    data = [
        case for case in data
        if case["id"] not in ["SMK-LOGIN-008", "SMK-LOGIN-009", "SMK-LOGIN-010", "SMK-LOGIN-011"]
    ]
        
    
    
    @pytest.mark.parametrize('case',data)
    
    def test_login(self,case,prepared_user):

        # ==============================
        # 1. 获取验证码
        # ==============================
        
        with allure.step(
            "1.获取并校验验证码"
        ):
            captcha_response = requests.get(
                BASE_URL + CAPTCHA_URL
            )
            #  HTTP 状态码
            #这里属于前置条件的断言，属于接口的前置条件，直接判断是否200，后期无需改动，不加入数据驱动
            assert captcha_response.status_code == 200
                
            captcha_data = captcha_response.json()
            
            assert captcha_data["code"] == 200
            
            # ==============================
            # 2. 提取 uuid
            # ==============================
            uuid = captcha_data.get("uuid")

            assert uuid, (
                "验证码接口未返回有效 uuid"
            )
            
            # ==============================
            # 3. Redis 获取验证码答案
            # ==============================
        with allure.step(
            "2.从 Redis 获取验证码答案"
        ):
            captcha_code = get_captcha_code(uuid)
            
            assert captcha_code, (
                f"Redis 中未获取到验证码，uuid={uuid}"
            )
            
        
            # ==============================
            # 4. 登录请求体
            # ==============================
            # Excel 中读取登录 Body
        with allure.step(
            "3.解析登录请求数据"
        ):
            login_data = ast.literal_eval(case["json"])
            
            # 动态添加验证码
            login_data["code"] = captcha_code
            login_data["uuid"] = uuid
            request_data = {
                "method": "post",
                "url": BASE_URL + LOGIN_URL,
                "headers": None,
                "params": None,
                "data": None,
                "json": login_data,
                "files": None,
            }
            
            # ==============================
            # 5. 调用登录接口
            # ==============================
            login_response, login_result = (
                execute_request(
                    request_data,
                    case["statusCode"],
                    case["id"]
                )
            )

            check_res_body = ast.literal_eval(case["check_res_body"])

            for res_key, res_value in check_res_body.items():
                assert res_key in login_result, (
                    f"响应中缺少字段：{res_key}"
        )
                actual_value = login_result[res_key]

                assert actual_value == res_value, (
                    f"{res_key}断言失败："
                    f"预期为 {res_value},"
                    f"实际为 {actual_value}"
                )
                
            # 只有预期登录成功时才检查 token
            if check_res_body.get("code") == 200:

                assert "token" in login_result, (
                    "登录成功但响应中没有token字段"
                )

                assert login_result["token"], (
                    "登录成功但token为空"
                )
                
        # ==============================
        # 打印执行结果
        # ==============================

        print("\n========== 登录接口执行结果 ==========")
        print(f"用例ID：{case['id']}")
        print(f"用例：{case['title']}")
        print(f"请求地址：{BASE_URL + LOGIN_URL}")
        print(f"用户名：{login_data.get('username')}")
        print("密码：******")
        print(f"HTTP状态码：{login_response.status_code}")

        print(
            f"业务响应："
            f"code={login_result.get('code')}, "
            f"msg={login_result.get('msg')}"
        )

        if (
            check_res_body.get("code") == 200
            and login_result.get("token")
        ):
            print("Token：获取成功")

        print("======================================\n")