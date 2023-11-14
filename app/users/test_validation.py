from unittest import TestCase
from unittest.mock import patch

from sqlalchemy import create_engine

from .validation import validate_user
from ..config import Settings

engine = create_engine(Settings(_env_file='test.env').database_url)


class DatabaseConnectionOverride:
    def __init__(self):
        self.connection = engine.connect()

    def __enter__(self):
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()


@patch("app.users.validation.DatabaseConnection", new=DatabaseConnectionOverride)
@patch("app.users.validation.is_password_valid")
@patch("app.users.validation.is_email_valid")
class ValidationTest(TestCase):

    def test_validate_user_invalid_email_and_password(self, mock_email, mock_password):
        mock_email.return_value = False
        mock_password.return_value = False
        email, password = ('email', 'pass')

        errors = validate_user(email, password)
        assert len(errors) == 2
        assert errors == ["Invalid email", "Invalid password"]

    def test_validate_user_invalid_email(self, mock_email, mock_password):
        mock_email.return_value = False
        mock_password.return_value = True
        email, password = ('email', 'password')

        errors = validate_user(email, password)
        assert len(errors) == 1
        assert errors == ["Invalid email"]

    def test_validate_user_invalid_password(self, mock_email, mock_password):
        mock_email.return_value = True
        mock_password.return_value = False
        email, password = ('email@domain.com', 'pass')

        errors = validate_user(email, password)
        assert len(errors) == 1
        assert errors == ["Invalid password"]

    def test_validate_user_invalid_password_and_existing_email(self, mock_email, mock_password):
        mock_email.return_value = True
        mock_password.return_value = False
        email, password = ('user@domain.com', 'password')

        errors = validate_user(email, password)
        assert len(errors) == 2
        assert errors == ["Invalid password", "An account with this email already exists"]

    def test_validate_user(self, mock_email, mock_password):
        mock_email.return_value = True
        mock_password.return_value = True
        email, password = ('email@domain.com', 'password')

        errors = validate_user(email, password)
        assert len(errors) == 0
