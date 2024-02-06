from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from lib.custom_exception import CustomException
from lib.twilio_functions import get_new_numbers, get_available_numbers, get_unused_phone_number
from lib.db import db

router = APIRouter(prefix="/phone")


class PhoneForm(BaseModel):
    user_id: str


async def assign_number(user_id: str, phone_number: str):
    try:
        await db.bot.create({"userId": user_id, "phone_no": phone_number, "refund_accept": "False"})
        return {"message": "Phone number assigned."}
    except Exception as e:
        raise CustomException("Error assigning phone number.", 500)


async def check_user(form: PhoneForm):
    user = await db.user.find_first(where={"id": form.user_id})
    if user is None:
        raise CustomException("User not found.", 401)


async def check_user_number(form: PhoneForm):
    user = await db.bot.find_first(where={"userId": form.user_id})
    if user is not None:
        raise CustomException("User already has a phone number.", 400)


@router.get("/new")
async def list_phones(form: PhoneForm):
    try:
        await check_user(form)
    except CustomException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

    phone_numbers = get_new_numbers()
    return {"message": "Available phone numbers.", "phone_numbers": phone_numbers}


@router.get("/available")
async def available_phones(form: PhoneForm):
    try:
        await check_user(form)
    except CustomException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

    phone_numbers = await get_available_numbers(get_first=False)
    return {"message": "Available phone numbers.", "phone_numbers": phone_numbers}


@router.get("/buy")
async def buy_phone(form: PhoneForm):
    try:
        await check_user(form)
        await check_user_number(form)
    except CustomException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

    phone_number = await get_unused_phone_number()
    try:
        await assign_number(form.user_id, phone_number)
    except CustomException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

    return {"message": "Phone number purchased.", "phone_number": phone_number}
