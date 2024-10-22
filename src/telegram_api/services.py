from config import TELEGRAM_BOT_ALLOWED_USERS


class InvalidUser(Exception):
    def __init__(self, user_id) -> None:
        super().__init__(f'User {user_id} is not allowed to enjoy this app.')


def user_verification(user_id: str):
    is_allowed = next(
        (allowed_user_id for allowed_user_id in TELEGRAM_BOT_ALLOWED_USERS if allowed_user_id == user_id), None
    )
    if not is_allowed:
        raise InvalidUser(user_id)
