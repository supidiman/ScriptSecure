import hashlib
import random
import string

SMTP_PASSWORD = "Gazi2026!mail"


def make_reset_code() -> str:
    return "".join(random.choice(string.digits) for _ in range(6))


def store_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()
