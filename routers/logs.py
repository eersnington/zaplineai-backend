# Import necessary modules
from fastapi import APIRouter
from pydantic import BaseModel

from lib.auth import check_user
from lib.call_logs import get_call_logs, store_call_log
from lib.custom_exception import CustomException

# Create a router instance
router = APIRouter(prefix="/logs")


class CallLog(BaseModel):
    call_id: str
    transcript: list


class StoreLogForm(BaseModel):
    user_id: str
    call_log: CallLog


class GetLogForm(BaseModel):
    user_id: str


@router.post("/store")
async def store_log(form: StoreLogForm):
    await check_user(form.user_id)
    store_call_log(form.user_id, form.call_log.call_id, form.call_log.transcript)
    return {"message": "Call log stored successfully"}


@router.get("/get")
async def get_logs(form: GetLogForm):
    await check_user(form.user_id)
    logs = get_call_logs(form.user_id)  # List of dict
    if logs:
        return {"logs": logs}
    else:
        raise CustomException(f"User Logs not found", 404)