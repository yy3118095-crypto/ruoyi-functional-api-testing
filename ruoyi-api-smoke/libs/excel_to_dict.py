#封装数据解析
import allure
import json as json_lib
import logging
import platform
from pathlib import Path
from libs.allure_request import (
    _hide_sensitive_data
)
from config.config import BASE_URL

@allure.step("1.解析请求数据")
def excel_to_dict(case):   
     #解析请求数据 
        #eval()-->把 Excel 中读取出来的“字符串”，转换成字典
        method = case["method"]
        url = BASE_URL + case["path"]
        headers = eval(case["headers"]) if isinstance(case["headers"], str)else None
        params = eval(case["params"]) if isinstance(case["params"], str) else None
        data = eval(case["data"]) if isinstance(case["data"], str) else None
        json = eval(case["json"]) if isinstance(case["json"], str) else None
        files = eval(case["files"]) if isinstance(case["files"], str) else None
        check_res_body = eval(case["check_res_body"]) if isinstance(case["check_res_body"], str) else None
    
    #组装成字典
        request_data = {
            "method": method,
            "url": url,
            "headers": headers,
            "params": params,
            "data": data,
            "json": json,
            "files": files,
       
        }
        #📚1.数据解析信息
    # ==============================
    # 添加解析后的请求数据附件
    # ==============================
        safe_request = _hide_sensitive_data(
            request_data
        )

        allure.attach(
            json_lib.dumps(
                safe_request,
                ensure_ascii=False,
                indent=2,
                default=str
            ),
            name="解析后的请求数据",
            attachment_type=(
                allure.attachment_type.JSON
            )
        )

        logging.info(
            f"数据解析信息：{safe_request}"
        )

        return (
            request_data,
            check_res_body
        )