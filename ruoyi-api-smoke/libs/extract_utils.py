import jsonpath


def extract_data(case, request_data, result, datas):

    if not case.get("jsonExData"):
        return

    extract_rules = eval(case["jsonExData"])

    for var_name, extract_path in extract_rules.items():

        # 方式1：从请求 JSON 中提取
        if extract_path.startswith("request.json."):

            field_name = extract_path.split(".")[-1]

            datas[var_name] = request_data["json"][field_name]

        # 方式2：从响应体 JSONPath 提取
        else:

            extract_result = jsonpath.jsonpath(
                result,
                extract_path
            )

            assert extract_result, (
                f"动态数据提取失败：{extract_path}"
            )

            datas[var_name] = extract_result[0]

        print(
            f"动态数据提取成功："
            f"{var_name}={datas[var_name]}"
        )