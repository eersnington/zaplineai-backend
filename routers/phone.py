import sqlite3
from fastapi import APIRouter
from pydantic import BaseModel

from lib.custom_exception import CustomException
from lib.twilio_functions import get_new_numbers, get_available_numbers, get_unused_phone_number
from lib.db import db
from lib.auth import check_user

router = APIRouter(prefix="/phone")


class PhoneForm(BaseModel):
    user_id: str


async def assign_number(user_id: str, phone_number: str):
    """
        Assigns a phone number to a user in the database.
    """
    try:
        await db.bot.create({"userId": user_id, "phone_no": phone_number, "refund_accept": "False"})
        return {"message": "Phone number assigned."}
    except Exception as e:
        raise CustomException("Error assigning phone number.", 500)


async def check_user_number(form: PhoneForm):
    """
        Checks if a user already has a phone number.
    """
    user = await db.bot.find_first(where={"userId": form.user_id})
    if user is not None:
        raise CustomException("User already has a phone number.", 400)


def initiatlize_user_metrics(user_id: str):
    """
        Initializes user metrics in the database.
    """
    sql = '''INSERT INTO user_metrics (user_id, calls, automated_calls, transferred_calls, abandoned_calls)
             VALUES (?, ?, ?, ?, ?)'''
    data = (user_id, 0, 0, 0, 0)

    conn = sqlite3.connect('user_metrics.db')
    c = conn.cursor()

    with conn:
        c.execute(sql, data)
        conn.commit()


@router.get("/new")
async def list_phones(form: PhoneForm):
    await check_user(form.user_id)

    phone_numbers = get_new_numbers()
    return {"message": "Available phone numbers.", "phone_numbers": phone_numbers}


@router.get("/available")
async def available_phones(form: PhoneForm):
    await check_user(form.user_id)

    phone_numbers = await get_available_numbers(get_first=False)
    return {"message": "Available phone numbers.", "phone_numbers": phone_numbers}


@router.post("/buy")
async def buy_phone(form: PhoneForm):
    await check_user(form.user_id)
    await check_user_number(form)

    phone_number = await get_unused_phone_number()
    try:
        await assign_number(form.user_id, phone_number)
        initiatlize_user_metrics(form.user_id)
    except Exception as e:
        raise CustomException(e.__str__, 500)

    return {"message": "Phone number purchased.", "phone_number": phone_number}
