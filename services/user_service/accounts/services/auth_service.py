from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.selectors.user_selector import get_user_by_email
from shared.common.exceptions import (
    AuthenticationFailedError,
    BadRequestError,
    ConflictError,
)

User = get_user_model()


def register_user(username: str, email: str, password: str,
                  first_name: str = '', last_name: str = ''):
    if User.objects.filter(username=username).exists():
        raise ConflictError(f"Username '{username}' is already taken.")
    if User.objects.filter(email=email).exists():
        raise ConflictError(f"Email '{email}' is already registered.")

    return User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )


def authenticate_user(email: str, password: str):
    user = get_user_by_email(email)
    if not user.check_password(password):
        raise AuthenticationFailedError("Invalid email or password.")
    if not user.is_active:
        raise AuthenticationFailedError("User account is disabled.")
    return user


def generate_tokens_for_user(user) -> dict:
    refresh = RefreshToken.for_user(user)
    refresh['username'] = user.username
    refresh['email'] = user.email
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def change_user_password(user, old_password: str, new_password: str) -> None:
    if not user.check_password(old_password):
        raise BadRequestError("Old password is incorrect.")
    user.set_password(new_password)
    user.save()
