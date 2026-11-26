"""
[主题]: JWT(HS256) 签发与校验 + 加盐密码哈希
[来源]: fastapi/full-stack-fastapi-template 后端安全模块（JWT 认证、密码哈希）
[难度]: Medium
[前置知识]: bytes 与 str、base64、hmac、hashlib、json

一、主题说明
JWT = base64url(header) . base64url(payload) . base64url(签名)。
签名用密钥对前两段做 HMAC-SHA256，服务端重新计算并比对，就能发现 payload 被篡改。
注意：payload 只是编码，不是加密，**不要把密码等机密放进去**。

二、解法对比
1. 直观版 hash_password_plain:
   - 直接 sha256(密码)。相同密码得到相同哈希，彩虹表一查就破，仅作反面教材。
2. 进阶版 hash_password / verify_password:
   - PBKDF2-HMAC-SHA256 + 随机盐 + 多轮迭代，每个用户哈希都不同，暴力破解成本高。
   - 比较使用 hmac.compare_digest，避免时序攻击。
   - 时间复杂度 O(迭代次数)，空间复杂度 O(1)

三、真实用途
- 全栈开发: 登录接口返回 access_token，后续请求带上它，服务端用 verify_jwt 识别用户。
- AI Agent / RAG: 给 /chat、/ingest 这类接口加认证与用量归属，是副业交付 AI 产品的基本盘。
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any


class InvalidTokenError(Exception):
    """令牌无效：格式错误、签名不符或已过期。"""


def b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b'=').decode('ascii')


def b64url_decode(text: str) -> bytes:
    padding = '=' * (-len(text) % 4)  # base64 长度必须是 4 的倍数，补齐 =
    return base64.urlsafe_b64decode(text + padding)


def _sign(signing_input: str, secret: str) -> str:
    digest = hmac.new(secret.encode('utf-8'), signing_input.encode('ascii'), hashlib.sha256).digest()
    return b64url_encode(digest)


def sign_jwt(payload: dict[str, Any], secret: str, ttl_seconds: int = 3600, now: float | None = None) -> str:
    """签发 JWT，自动写入 exp（过期时间戳）。"""
    issued_at = int(time.time() if now is None else now)
    body = {**payload, 'exp': issued_at + ttl_seconds}
    header = {'alg': 'HS256', 'typ': 'JWT'}
    dump = lambda data: json.dumps(data, separators=(',', ':'), sort_keys=True).encode('utf-8')  # noqa: E731
    signing_input = f'{b64url_encode(dump(header))}.{b64url_encode(dump(body))}'
    return f'{signing_input}.{_sign(signing_input, secret)}'


def verify_jwt(token: str, secret: str, now: float | None = None) -> dict[str, Any]:
    """校验签名与过期时间，通过则返回 payload。"""
    parts = token.split('.')
    if len(parts) != 3:
        raise InvalidTokenError('令牌格式错误')
    signing_input = f'{parts[0]}.{parts[1]}'
    if not hmac.compare_digest(_sign(signing_input, secret), parts[2]):
        raise InvalidTokenError('签名不匹配')
    try:
        payload = json.loads(b64url_decode(parts[1]))
    except ValueError as exc:
        raise InvalidTokenError('payload 无法解析') from exc
    current = time.time() if now is None else now
    if payload.get('exp', 0) <= current:
        raise InvalidTokenError('令牌已过期')
    return payload


def hash_password_plain(password: str) -> str:
    """反面教材：无盐 sha256。"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def hash_password(password: str, salt: bytes | None = None, iterations: int = 60_000) -> str:
    """加盐 + 多轮迭代的 PBKDF2 哈希，格式: pbkdf2_sha256$迭代$盐$哈希。"""
    salt = os.urandom(16) if salt is None else salt
    digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
    return f'pbkdf2_sha256${iterations}${salt.hex()}${digest.hex()}'


def verify_password(password: str, stored: str) -> bool:
    try:
        _, iterations, salt_hex, hash_hex = stored.split('$')
        digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt_hex), int(iterations))
    except ValueError:
        return False
    return hmac.compare_digest(digest.hex(), hash_hex)


def run_tests() -> None:
    """自动化断言测试。"""
    secret = 'unit-test-secret'
    token = sign_jwt({'sub': 'alice'}, secret, ttl_seconds=60, now=1_000)
    assert verify_jwt(token, secret, now=1_030)['sub'] == 'alice'

    # 过期
    try:
        verify_jwt(token, secret, now=1_061)
    except InvalidTokenError as exc:
        assert '过期' in str(exc)
    else:
        raise AssertionError('过期令牌必须被拒绝')

    # 密钥错误
    try:
        verify_jwt(token, 'wrong-secret', now=1_030)
    except InvalidTokenError as exc:
        assert '签名' in str(exc)
    else:
        raise AssertionError('错误密钥必须被拒绝')

    # 篡改 payload（把 alice 改成 admin 但保留旧签名）
    header, _, signature = token.split('.')
    forged_payload = b64url_encode(json.dumps({'sub': 'admin', 'exp': 9_999_999_999}).encode('utf-8'))
    try:
        verify_jwt(f'{header}.{forged_payload}.{signature}', secret, now=1_030)
    except InvalidTokenError:
        pass
    else:
        raise AssertionError('被篡改的令牌必须被拒绝')

    try:
        verify_jwt('abc.def', secret)
    except InvalidTokenError:
        pass
    else:
        raise AssertionError('格式错误必须被拒绝')

    # 密码：无盐哈希相同，加盐哈希不同但都能验证
    assert hash_password_plain('pw') == hash_password_plain('pw')
    first, second = hash_password('pw'), hash_password('pw')
    assert first != second
    assert verify_password('pw', first) and verify_password('pw', second)
    assert not verify_password('wrong', first)
    assert not verify_password('pw', 'garbage')
    print('✅ JWT 与密码哈希所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} JWT 与密码哈希 {'*' * 12}", sep='', end='\n\n')
    token = sign_jwt({'sub': 'alice'}, 'demo-secret', ttl_seconds=60, now=1_000)
    print(f'token: {token}')
    print(f'校验通过的 payload: {verify_jwt(token, "demo-secret", now=1_010)}')
    print(f'加盐哈希: {hash_password("my-password")[:48]}...')
    run_tests()


if __name__ == '__main__':
    bootstrap()
