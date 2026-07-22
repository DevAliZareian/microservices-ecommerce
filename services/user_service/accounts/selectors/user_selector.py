from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from accounts.models import Profile

User = get_user_model()

def get_user_by_id(user_id: int):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        from accounts.shared.exceptions import NotFoundError
        raise NotFoundError(f"User with id {user_id} not found.")

def get_user_by_username(username: str):
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        from accounts.shared.exceptions import NotFoundError
        raise NotFoundError(f"User '{username}' not found.")

def get_user_by_email(email: str):
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        from accounts.shared.exceptions import NotFoundError
        raise NotFoundError(f"User with email {email} not found.")

def get_profile_by_user(user) -> Profile:
    try:
        return user.profile
    except ObjectDoesNotExist:
        from accounts.shared.exceptions import NotFoundError
        raise NotFoundError(f"Profile for user '{user.username}' not found.")

def filter_users_active(**filters):
    return User.objects.filter(is_active=True, **filters)