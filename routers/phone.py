from fastapi import APIRouter, Request, Response
from lib.twilio_functions import get_phone_numbers, get_unused_phone_number

router = APIRouter(prefix="/phone")


@router.get("/list")
async def list_phones():
    phone_numbers = get_phone_numbers()
    return {"message": "Available Phone Numbers", "phone_numbers": phone_numbers}


@router.get("/buy")
async def buy_phone():
    phone_number = get_unused_phone_number()

    return {"message": "Phone number purchased.", "phone_number": phone_number}
