import re
from .code_generator import generate_activation_code

code_regex = re.compile(r"[0-9]{4}")


def test_generate_activation_code():
    for _ in range(1000):
        code = generate_activation_code()
        assert re.fullmatch(code_regex, code) is not None
