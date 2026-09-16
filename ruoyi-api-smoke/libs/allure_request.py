import json
import allure
import requests

'''
1. 发送真实接口请求
2. 把请求和响应添加到 Allure 报告
3. 展示请求数据前隐藏 token、密码等敏感信息
'''
def _hide_sensitive_data(
    request_data
):
    """
    复制请求数据，并隐藏 token。
    不修改真正发送的请求。
    """

    safe_request = dict(
        request_data
    )
# 请求头脱敏
    headers = dict(
        request_data.get("headers")
        or {}
    )

    if "Authorization" in headers:
        headers["Authorization"] = (
            "Bearer ******"
        )

    safe_request["headers"] = headers
    
     # 请求体脱敏
    json_data = dict(
        request_data.get("json")
        or {}
    )

    for key in json_data:

        if key.lower() in [
            "password",
            "code",
            "token"
        ]:
            json_data[key] = "******"

    safe_request["json"] = json_data
    
    return safe_request


def execute_request(
    request_data,
    expected_status,
    case_id
):
    """
    发送接口请求、添加 Allure 附件，
    并校验 HTTP 状态码。
    """

    method = (
        request_data
        .get("method", "")
        .upper()
    )

    url = request_data.get("url")

    # ==============================
    # 1. 发送请求
    # ==============================
    with allure.step(
        f"发送接口请求：{method} {url}"
    ):
        safe_request = (
            _hide_sensitive_data(
                request_data
            )
        )

        allure.attach(
            json.dumps(
                safe_request,
                ensure_ascii=False,
                indent=2,
                default=str
            ),
            name="实际请求数据",
            attachment_type=(
                allure.attachment_type.JSON
            )
        )

        response = requests.request(
            **request_data
        )

        try:
            result = response.json()

            allure.attach(
                json.dumps(
                    result,
                    ensure_ascii=False,
                    indent=2,
                    default=str
                ),
                name="实际响应数据",
                attachment_type=(
                    allure.attachment_type.JSON
                )
            )

        except ValueError:
            result = None

            allure.attach(
                response.text,
                name="实际响应内容",
                attachment_type=(
                    allure.attachment_type.TEXT
                )
            )

    # ==============================
    # 2. HTTP 状态码断言
    # ==============================
    with allure.step(
        f"校验 HTTP 状态码："
        f"预期 {expected_status}，"
        f"实际 {response.status_code}"
    ):
        assert (
            response.status_code
            == int(expected_status)
        ), (
            f"{case_id} HTTP状态码错误："
            f"预期={expected_status}，"
            f"实际={response.status_code}"
        )

    # ==============================
    # 3. 确认响应是 JSON
    # ==============================
    with allure.step(
        "确认接口返回 JSON 数据"
    ):
        assert result is not None, (
            f"{case_id} 接口没有返回JSON："
            f"{response.text}"
        )

    return response, result


def parse_response(
    response,
    attachment_name="实际响应数据"
):
    """
    解析接口响应，并添加到 Allure。
    """

    with allure.step(
        f"解析响应数据：{attachment_name}"
    ):

        try:
            result = response.json()

        except ValueError:

            allure.attach(
                response.text,
                name="非JSON响应内容",
                attachment_type=(
                    allure.attachment_type.TEXT
                )
            )

            raise AssertionError(
                "接口响应不是有效的 JSON："
                f"{response.text}"
            )

        allure.attach(
            json.dumps(
                result,
                ensure_ascii=False,
                indent=2,
                default=str
            ),
            name=attachment_name,
            attachment_type=(
                allure.attachment_type.JSON
            )
        )

        return result
    
def _hide_response_sensitive_data(
    result
):
    """
    隐藏响应中的 token。
    """

    if not isinstance(result, dict):
        return result

    safe_result = dict(result)

    for key in safe_result:

        if key.lower() in [
            "token",
            "access_token",
            "refresh_token"
        ]:
            safe_result[key] = "******"

    return safe_result