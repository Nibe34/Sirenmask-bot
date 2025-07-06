from sirenmask.config import ALLOWED_USERS

def is_authorized(user_id: int) -> bool:
    #return user_id in ALLOWED_USERS
    return True         # поки що вимкнув вайтліст, не впевнений що ця функція потрібна. може, в майбутньому тут буде якась бізнес логіка
