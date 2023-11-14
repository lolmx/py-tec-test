import hashlib
import re

# Let's say at least 6 alphanumeric only characters
password_regex = re.compile(r"[A-Za-z0-9]{6,}")


def is_password_valid(password: str) -> bool:
    return re.fullmatch(password_regex, password) is not None


def encode_password(password: str) -> str:
    sha256 = hashlib.sha256()
    sha256.update(password.encode())

    return sha256.hexdigest()
