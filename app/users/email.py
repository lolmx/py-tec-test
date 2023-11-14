from datetime import datetime, timedelta

from sqlalchemy import text

from ..database import DatabaseConnection
from ..utils.code_generator import generate_activation_code
from ..utils.email import send_email


async def send_activation_email(email: str):
    code = generate_activation_code()

    await send_email(email, f"Your activation code is {code}")

    expiration = datetime.now() + timedelta(minutes=1)

    with DatabaseConnection() as db_con:
        q = text("UPDATE users SET activation_code=:code, activation_code_expiration=:expiration WHERE email=:email")
        db_con.execute(q, {"email": email, "code": code, "expiration": expiration})
        db_con.commit()
