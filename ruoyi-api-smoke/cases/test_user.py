import redis
import requests
import pytest
import jsonpath
import ast
from jinja2 import Template
import allure

from libs.allure_request import (
    parse_response
)

from libs.global_data import datas
from libs.excel_utils import read_excel
from config.config import *
from libs.excel_to_dict import excel_to_dict
from libs.extract_utils import extract_data

#用户管理接口
class Test_user:
    #读测试数据
    data = read_excel(sheet_name="user")
    
    #用户管理-->查询接口
    @pytest.mark.parametrize('case',data)
    def test_user_list(self,case,admin_token):
        # ==============================
        # 2. 替换Excel中的 {{TOKEN}}
        # ==============================
        case = ast.literal_eval(
            Template(str(case)).render(datas)
        )
        
        # ==============================
        # 3. Excel -> requests参数
        # ==============================
        request_data, check_res_body = excel_to_dict(case)

        # ==============================
        # 4. 发送请求
        # ==============================
        response = requests.request(
            **request_data
        )

        result = parse_response(
            response
        )

        # ==============================
        # 5. HTTP状态码断言
        # ==============================
        assert response.status_code == int(
            case["statusCode"]
        ), (
            f"HTTP状态码断言失败："
            f"预期={case['statusCode']}，"
            f"实际={response.status_code}"
        )

        # ==============================
        # 6. 响应断言
        # ==============================
        for key, expected_value in check_res_body.items():

            # ==============================
            # 1. JSONPath断言
            # ==============================
            if key.startswith("$"):

                actual_result = jsonpath.jsonpath(
                    result,
                    key
                )

                assert actual_result, (
                    f"JSONPath未找到数据：{key}"
                )

                actual_value = actual_result[0]

            # ==============================
            # 2. 普通字段断言
            # ==============================
            else:

                assert key in result, (
                    f"响应中缺少字段：{key}"
                )

                actual_value = result[key]

            # ==============================
            # 3. 值断言
            # ==============================
            assert actual_value == expected_value, (
                f"{key}断言失败："
                f"预期={expected_value}，"
                f"实际={actual_value}"
            )
            
        #  动态数据提取
        extract_data(
            case,
            request_data,
            result,
            datas
            
        )
            
        print(
            f"【{case['id']}】动态数据：",
            datas
        )


        # ==============================
        # 7. action区分二次业务校验
        # ==============================

        action = case["action"]

        if action == "list":
            pass

        elif action == "add":

            # 新增成功后，确认请求体中存在 userName
            user_name = request_data["json"].get("userName")

            assert user_name, "新增用户请求中缺少 userName"

            print(f"新增用户成功：userName={user_name}")

        
        elif action == "update":
            # 1. 获取本次修改使用的数据
            update_json = request_data.get(
                "json",
                {}
            )

            user_name = update_json.get(
                "userName"
            )

            expected_nick_name = update_json.get(
                "nickName"
            )

            assert user_name, (
                "修改用户请求中缺少 userName"
            )

            assert expected_nick_name, (
                "修改用户请求中缺少 nickName"
            )

            # 2. 修改后重新查询用户
            check_response = requests.get(
                BASE_URL + USER_LIST_URL,
                headers={
                    "Authorization": (
                        f"Bearer {datas['TOKEN']}"
                    )
                },
                params={
                    "userName": user_name
                }
            )

            assert check_response.status_code == 200, (
                f"修改后二次查询HTTP状态码异常："
                f"{check_response.status_code}"
            )

            check_result = check_response.json()

            assert check_result.get("code") == 200, (
                f"修改后二次查询失败："
                f"{check_result}"
            )

            # 3. 精确找到目标用户
            user = next(
                (
                    row
                    for row in check_result.get(
                        "rows",
                        []
                    )
                    if row.get("userName")
                    == user_name
                ),
                None
            )

            assert user, (
                f"修改后未查询到用户："
                f"{user_name}"
            )

            # 4. 校验修改后的昵称
            actual_nick_name = user.get(
                "nickName"
            )

            assert (
                actual_nick_name
                == expected_nick_name
            ), (
                f"昵称修改未生效："
                f"预期={expected_nick_name}，"
                f"实际={actual_nick_name}"
            )

        elif action == "delete":
            pass



        # ==============================
        # 打印结果
        # ==============================
        rows = result.get("rows", [])

        user_names = [
            user.get("userName")
            for user in rows
        ]
        
        nick_names = [
            user.get("nickName")
            for user in rows
        ]

        print(
            "\n========== 用户管理接口执行结果 =========="
        )

        print(
            f"用例ID：{case['id']}"
        )

        print(
            f"用例：{case['title']}"
        )

        print(
            f"请求方式：{request_data.get('method')}"
        )

        print(
            f"请求地址：{request_data.get('url')}"
        )

        print(
            f"请求头：{request_data.get('headers')}"
        )

        print(
            f"请求参数：{request_data.get('params')}"
        )

        print(
            f"请求体：{request_data.get('json')}"
        )

        print(
            f"HTTP状态码：{response.status_code}"
        )

        print(
            f"业务响应："
            f"code={result.get('code')}, "
            f"msg={result.get('msg')}, "
            f"total={result.get('total')}, "
            f"userName={user_names}, "
            f"nickName={nick_names}"
        )

        print(
            "===========================================\n"
        )
        
        
        
        
        
