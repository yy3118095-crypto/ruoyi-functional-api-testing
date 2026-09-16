import requests
import pytest
from jinja2 import Template
import ast
import allure
from libs.allure_request import (
    parse_response
)

from libs.global_data import datas
from libs.excel_utils import read_excel
from config.config import *
from libs.excel_to_dict import excel_to_dict
from libs.extract_utils import extract_data
from libs.assert_response import assert_response

#角色管理接口
class Test_role:
    #读测试数据
    data = read_excel(sheet_name="role")
    
    #角色管理接口
    @pytest.mark.parametrize('case',data)
    def test_role_api(self,case,admin_token):
        
        # ==============================
        # 1. 准备动态数据
        # ==============================
        case = ast.literal_eval(
        Template(str(case)).render(datas)
    )
        
        # ==============================
        # Excel -> requests参数
        # ==============================
        request_data, check_res_body = excel_to_dict(case)

        # ==============================
        # 发送请求
        # ==============================
        response = requests.request(
            **request_data)

        result = parse_response(
            response
        )

        # ==============================
        # HTTP状态码断言
        # ==============================
        assert response.status_code == int(
            case["statusCode"]
        )

        # ==============================
        # 响应断言
        # ==============================
        assert_response(
            result,
            check_res_body
        )
            
        #  动态数据提取
        extract_data(
            case,
            request_data,
            result,
            datas
)

        
        action = case["action"]

        if action == "list":
            pass

        elif action == "add":

            # 新增成功后，确认请求体中存在 roleName
            role_name = request_data["json"].get("roleName")

            assert role_name, "新增角色请求中缺少 roleName"

            print(f"新增角色成功：roleName={role_name}")

        
        elif action == "update":
            pass

        elif action == "delete":
            pass
 
        # ==============================
        # 8. 打印结果
        # ==============================
        rows = result.get("rows", [])

        role_names = [
            role.get("roleName")
            for role in rows
        ]
        
        nick_names = [
            role.get("nickName")
            for role in rows
        ]

        print("\n========== 角色查询接口执行结果 ==========") 
        print(f"用例：{case['title']}")
        print(f"请求头：{request_data.get('headers')}")
        print(f"请求参数：{request_data.get('params')}")
        print(f"HTTP状态码：{response.status_code}")
        print(
            f"业务响应："
            f"code={result.get('code')}, "
            f"msg={result.get('msg')}, "
            f"total={result.get('total')}，"
            f"roleName={role_names}"
        )
        print("=========================================\n")
        
        
        
        
        
