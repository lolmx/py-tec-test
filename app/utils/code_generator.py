import string
from random import choice


def generate_activation_code() -> str:
    numbers = string.digits
    rand = "".join(choice(numbers) for _ in range(4))

    return rand
