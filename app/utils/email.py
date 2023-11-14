import re

# Simplifying a bit an email address definition
# +_-. are the only special characters allowed in the local part
# '.' can't be at the beginning or end, and there can't be two consecutive '.' (other special characters can!)
# tld in the domain part can only be lowercase alphabetic characters
# no length restrictions
email_regex = re.compile(r"([0-9a-zA-Z+_-]+(\.[0-9a-zA-Z+_-]+)*)@([0-9a-zA-Z]+(\.[0-9a-zA-Z]+)*(\.[a-z]+))")


def is_email_valid(email: str) -> bool:
    return re.fullmatch(email_regex, email) is not None


# This is our third party provider
async def send_email(email: str, content: str):
    print(email + ": " + content)
