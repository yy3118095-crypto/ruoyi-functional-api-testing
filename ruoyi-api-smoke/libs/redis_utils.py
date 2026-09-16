import redis


def get_captcha_code(uuid):
    """
    根据验证码 uuid 从 Redis 获取验证码答案
    """

    redis_client = redis.Redis(
        host="localhost",
        port=6379,
        db=0,
        decode_responses=True
    )

    captcha_code = redis_client.get(
        f"captcha_codes:{uuid}"
    )

    assert captcha_code is not None, (
        f"Redis中未获取到验证码，uuid={uuid}"
    )

    # Redis 返回值类似 '"1"'，去掉两端多余的双引号
    captcha_code = captcha_code.strip('"')

    return captcha_code