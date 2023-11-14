from datetime import datetime
from unittest.mock import patch

from pytest import mark
from sqlalchemy import create_engine, text

from .email import send_activation_email
from ..config import Settings

engine = create_engine(Settings(_env_file='test.env').database_url)


class DatabaseConnectionOverride:
    def __init__(self):
        self.connection = engine.connect()

    def __enter__(self):
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()


@mark.asyncio
@patch("app.users.email.DatabaseConnection", new=DatabaseConnectionOverride)
@patch("app.users.email.datetime")
@patch("app.users.email.send_email")
@patch("app.users.email.generate_activation_code")
async def test_send_activation_email(mock_generator, mock_mailer, mock_datetime):
    test_email = 'user@domain.com'
    test_code = '6789'
    now = datetime(year=2023, month=11, day=12, hour=16, minute=30, second=15)
    expected_expiration = datetime(year=2023, month=11, day=12, hour=16, minute=31, second=15)
    mock_generator.return_value = test_code
    mock_datetime.now.return_value = now

    await send_activation_email('user@domain.com')

    mock_mailer.assert_called_once_with(test_email, "Your activation code is 6789")

    with DatabaseConnectionOverride() as db_con:
        q = text("SELECT * FROM users WHERE email=:email")
        res = db_con.execute(q, {"email": test_email})
    db_user = res.mappings().first()
    assert db_user.get('activation_code') == test_code
    assert db_user.get('activation_code_expiration') == expected_expiration

    # Tear down
    with DatabaseConnectionOverride() as db_con:
        q = text("UPDATE users SET activation_code=:code WHERE email=:email")
        db_con.execute(q, {"email": test_email, "code": "1234"})
        db_con.commit()
