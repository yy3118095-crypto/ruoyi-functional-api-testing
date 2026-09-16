import jsonpath


def assert_response(result, check_res_body):

    for key, expected_value in check_res_body.items():

        # ==============================
        # 1. JSONPath
        # ==============================
        if key.startswith("$"):

            actual_result = jsonpath.jsonpath(
                result,
                key
            )

            assert actual_result, (
                f"JSONPath未找到数据：{key}"
            )
            
            # ==============================
            # all_equal：所有结果都等于指定值
            # ==============================
            if (
                isinstance(expected_value, dict)
                and "all_equal" in expected_value
            ):
                expected = expected_value["all_equal"]

                assert all(
                    value == expected
                    for value in actual_result
                ), (
                    f"{key} 数据权限断言失败："
                    f"预期所有值={expected}，"
                    f"实际={actual_result}"
                )

                continue
            
            # 原来的普通 JSONPath 断言
            actual_value = actual_result[0]

            assert actual_value == expected_value, (
                f"{key}断言失败："
                f"预期={expected_value}，"
                f"实际={actual_value}"
            )

            continue

        # ==============================
        # 2. 普通字段存在性检查
        # ==============================
        assert key in result, (
            f"响应中缺少字段：{key}"
        )

        actual_value = result[key]

        # ==============================
        # 3. contains / not_contains
        # ==============================
        if isinstance(expected_value, dict):

            if "contains" in expected_value:

                for value in expected_value["contains"]:

                    assert value in actual_value, (
                        f"{key} 中缺少：{value}，"
                        f"实际={actual_value}"
                    )

            if "not_contains" in expected_value:

                for value in expected_value["not_contains"]:

                    assert value not in actual_value, (
                        f"{key} 中不应该包含：{value}，"
                        f"实际={actual_value}"
                    )

            continue

        # ==============================
        # 4. 普通相等断言
        # ==============================
        assert actual_value == expected_value, (
            f"{key}断言失败："
            f"预期={expected_value}，"
            f"实际={actual_value}"
        )