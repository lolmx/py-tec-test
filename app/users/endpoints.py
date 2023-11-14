import secrets
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Body, status, BackgroundTasks, Response
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import text

from .email import send_activation_email
from .password import encode_password
from .validation import validate_user
from ..database import DatabaseConnection

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

security = HTTPBasic()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
        email: Annotated[str, Body()],
        password: Annotated[str, Body()],
        background_tasks: BackgroundTasks
):
    validation_errors = validate_user(email, password)
    if len(validation_errors) != 0:
        raise RequestValidationError(errors=validation_errors)

    with DatabaseConnection() as db_con:
        q = text("INSERT INTO users (email, password) VALUE (:email, :password)")
        db_con.execute(q, {"email": email, "password": encode_password(password)})
        db_con.commit()

    background_tasks.add_task(send_activation_email, email)

    return {"message": "Check your emails to activate your account"}


@router.post("/me/activate")
async def activate_user(
        activation_code: Annotated[str, Body()],
        credentials: Annotated[HTTPBasicCredentials, Depends(security)],
        response: Response
):
    with DatabaseConnection() as db_con:
        q = text("SELECT password, activated, activation_code, activation_code_expiration FROM users WHERE email=:email")
        res = db_con.execute(q, {"email": credentials.username})
    if not res.rowcount == 1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user = res.mappings().first()

    is_password_correct = secrets.compare_digest(encode_password(credentials.password), user.get('password'))
    if not is_password_correct:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if user.get('activated'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already activated")

    if datetime.now() > user.get('activation_code_expiration'):
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Activation code expired")

    if not secrets.compare_digest(activation_code, user.get('activation_code')):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Wrong activation code")

    with DatabaseConnection() as db_con:
        q = text("UPDATE users SET activated=1 WHERE email=:email")
        db_con.execute(q, {"email": credentials.username})
        db_con.commit()

    response.status_code = status.HTTP_204_NO_CONTENT
