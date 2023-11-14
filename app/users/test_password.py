from pytest import mark

from .password import is_password_valid, encode_password


@mark.parametrize(
    "password, result",
    [
        ('12345', False),
        ('passw', False),
        ('PASSW', False),
        ('1AbC2', False),
        ('passwo', True),
        ('123456', True),
        ('PASSWO', True),
        ('12abCD', True),
        ('12@bCD', False),
    ]
)
def test_is_password_valid(password, result):
    assert is_password_valid(password) is result


def test_encode_password():
    assert encode_password('password') == '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'
