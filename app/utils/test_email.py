from pytest import mark

from .email import is_email_valid


@mark.parametrize(
    "email, result",
    [
        ('notvalid', False),
        ('notvalid@', False),
        ('notvalid@domain', False),
        ('notvalid@domain.', False),
        ('notvalid@.domain', False),
        ('notvalid@.domain.com', False),
        ('notvalid@domain..com', False),
        ('notvalid@domain.c0m', False),
        ('valid@domain.com', True),
        ('VALID@domain.com', True),
        ('valid@sub.domain.xyz', True),
        ('_valid@domain.com', True),
        ('-valid@domain.com', True),
        ('+valid@domain.com', True),
        ('v4l1d@domain.com', True),
        ('1234@dom41n.com', True),
        ('still.valid@domain.com', True),
        ('still+valid@domain.com', True),
        ('still-valid@domain.com', True),
        ('.notvalid@domain.com', False),
        ('notvalid.@domain.com', False),
        ('not..valid@domain.com', False),
    ]
)
def test_is_password_valid(email, result):
    assert is_email_valid(email) is result
