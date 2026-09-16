import requests

from config.config import (
    BASE_URL,
    CAPTCHA_URL,
    LOGIN_URL,
)

from libs.redis_utils import get_captcha_code


def login(username, password):

    # 1. 获取验证码
    captcha_response = requests.get(
        BASE_URL + CAPTCHA_URL
    )

    assert captcha_response.status_code == 200

    captcha_data = captcha_response.json()

    assert captcha_data.get("code") == 200

    # 2. 获取 uuid
    uuid = captcha_data.get("uuid")

    assert uuid, (
        "登录前未获取到验证码 uuid"
    )

    # 3. 从 Redis 获取验证码
    captcha_code = get_captcha_code(uuid)

    assert captcha_code, (
        f"Redis 中未获取到验证码：uuid={uuid}"
    )

    # 4. 登录
    response = requests.post(
        BASE_URL + LOGIN_URL,
        json={
            "username": username,
            "password": password,
            "code": captcha_code,
            "uuid": uuid,
        }
    )

    return response