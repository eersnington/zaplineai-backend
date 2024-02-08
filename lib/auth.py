from lib.db import db
from lib.custom_exception import CustomException

async def check_user(user_id: str):
    user = await db.user.find_first(where={"id": user_id})
    if user is None:
        raise CustomException("User not found.", 401)