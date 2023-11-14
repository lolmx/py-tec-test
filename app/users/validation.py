from sqlalchemy import text

from .password import is_password_valid
from ..database import DatabaseConnection
from ..utils.email import is_email_valid


def validate_user(email: str, password: str):
    err = []
    check_db_for_email = True

    if not is_email_valid(email):
        err.append("Invalid email")
        check_db_for_email = False

    if not is_password_valid(password):
        err.append("Invalid password")

    if check_db_for_email:
        with DatabaseConnection() as db_con:
            q = text("SELECT email FROM users WHERE email=:email")
            res = db_con.execute(q, {"email": email})
        if res.rowcount != 0:
            err.append("An account with this email already exists")

    return err
