from datetime import datetime, timedelta
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from .email import send_activation_email
from .password import encode_password
from ..config import Settings
from ..main import app

client = TestClient(app)

engine = create_engine(Settings(_env_file='test.env').database_url)


class DatabaseConnectionOverride:
    def __init__(self):
        self.connection = engine.connect()

    def __enter__(self):
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()


def test_create_user_bad_email():
    response = client.post(
        "/users",
        json={"email": "notvalid", "password": "validpassword"}
    )
    assert response.status_code == 422
    assert response.json() == {"detail": ["Invalid email"]}


def test_create_user_bad_password():
    response = client.post(
        "/users",
        json={"email": "valid@email.com", "password": "noop"}
    )
    assert response.status_code == 422
    assert response.json() == {"detail": ["Invalid password"]}


def test_create_user_bad_email_and_password():
    response = client.post(
        "/users",
        json={"email": "notvalid", "password": "noop"}
    )
    assert response.status_code == 422
    assert response.json() == {"detail": ["Invalid email", "Invalid password"]}


@patch("app.users.validation.DatabaseConnection", new=DatabaseConnectionOverride)
def test_create_user_email_already_exists():
    response = client.post(
        "/users",
        json={"email": "user@domain.com", "password": "validpassword"}
    )
    assert response.status_code == 422
    assert response.json() == {"detail": ["An account with this email already exists"]}


@patch("app.users.validation.DatabaseConnection", new=DatabaseConnectionOverride)
@patch("app.users.endpoints.DatabaseConnection", new=DatabaseConnectionOverride)
@patch("fastapi.background.BackgroundTasks.add_task")
def test_create_user(mock_tasks):
    test_email = "user2@domain.com"
    test_password = "validpassword"

    response = client.post(
        "/users",
        json={"email": test_email, "password": test_password}
    )
    assert response.status_code == 201
    assert response.json() == {"message": "Check your emails to activate your account"}

    mock_tasks.assert_called_once_with(send_activation_email, test_email)

    with DatabaseConnectionOverride() as db_con:
        q = text("SELECT * FROM users WHERE email=:email")
        res = db_con.execute(q, {"email": test_email})
    assert res.rowcount == 1
    db_user = res.mappings().first()
    assert db_user.get('email') == test_email
    assert db_user.get('password') == encode_password(test_password)
    assert db_user.get('activated') == 0

    # Tear down
    with DatabaseConnectionOverride() as db_con:
        q = text("DELETE FROM users WHERE email=:email")
        db_con.execute(q, {"email": test_email})
        db_con.commit()


def test_activate_user_no_auth():
    response = client.post(
        "/users/me/activate"
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


@patch("app.users.endpoints.DatabaseConnection", new=DatabaseConnectionOverride)
def test_activate_user_unknown_email():
    test_email = "user2@domain.com"
    test_password = "password"

    response = client.post(
        "/users/me/activate",
        auth=(test_email, test_password),
        content="\"1234\""
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}


@patch("app.users.endpoints.DatabaseConnection", new=DatabaseConnectionOverride)
def test_activate_user_wrong_password():
    test_email = "user@domain.com"
    test_password = "wrongpassword"

    response = client.post(
        "/users/me/activate",
        auth=(test_email, test_password),
        content="\"1234\""
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}


@patch("app.users.endpoints.DatabaseConnection", new=DatabaseConnectionOverride)
def test_activate_user_already_activated():
    test_email = "activated@domain.com"
    test_password = "password"

    response = client.post(
        "/users/me/activate",
        auth=(test_email, test_password),
        content="\"1234\""
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "User already activated"}


@patch("app.users.endpoints.DatabaseConnection", new=DatabaseConnectionOverride)
def test_activate_user_activation_code_expired():
    test_email = "user@domain.com"
    test_password = "password"
    expiration = datetime.now() - timedelta(seconds=1)
    with DatabaseConnectionOverride() as db_con:
        q = text("UPDATE users SET activation_code_expiration=:expiration WHERE email=:email")
        db_con.execute(q, {"email": test_email, "expiration": expiration})
        db_con.commit()

    response = client.post(
        "/users/me/activate",
        auth=(test_email, test_password),
        content="\"1234\""
    )
    assert response.status_code == 410
    assert response.json() == {"detail": "Activation code expired"}


@patch("app.users.endpoints.DatabaseConnection", new=DatabaseConnectionOverride)
def test_activate_user_wrong_activation_code():
    test_email = "user@domain.com"
    test_password = "password"
    expiration = datetime.now() + timedelta(seconds=1)
    with DatabaseConnectionOverride() as db_con:
        q = text("UPDATE users SET activation_code_expiration=:expiration WHERE email=:email")
        db_con.execute(q, {"email": test_email, "expiration": expiration})
        db_con.commit()

    response = client.post(
        "/users/me/activate",
        auth=(test_email, test_password),
        content="\"4444\""
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Wrong activation code"}


@patch("app.users.endpoints.DatabaseConnection", new=DatabaseConnectionOverride)
def test_activate_user():
    test_email = "user@domain.com"
    test_password = "password"
    expiration = datetime.now() + timedelta(seconds=1)
    with DatabaseConnectionOverride() as db_con:
        q = text("UPDATE users SET activation_code_expiration=:expiration WHERE email=:email")
        db_con.execute(q, {"email": test_email, "expiration": expiration})
        db_con.commit()

    response = client.post(
        "/users/me/activate",
        auth=(test_email, test_password),
        content="\"1234\""
    )
    assert response.status_code == 204

    # Tear down
    with DatabaseConnectionOverride() as db_con:
        q = text("UPDATE users SET activated=0 WHERE email=:email")
        db_con.execute(q, {"email": test_email})
        db_con.commit()
