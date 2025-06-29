from sirenmask.config import ALLOWED_USERS

def is_authorized(user_id: int) -> bool:
    return user_id in ALLOWED_USERS
