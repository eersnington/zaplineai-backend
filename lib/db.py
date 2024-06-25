import asyncio
import datetime
import json
from prisma import Prisma

from prisma.fields import Json

db = Prisma()

async def track_metrics(user_id: str, call_type: str, call_intent: str) -> None:
    """
    Tracks the metrics of a user's call.

    Args:
    - user_id (str): The user's ID.
    - call_type (str): The type of call to be tracked.
    - call_intent (str): The intent of the call.

    Returns:
        None. The function performs an insert operation and does not return anything.
    """


    if call_type == "automated":
        await db.callstats.update(
            where={
                'user_id': user_id,
            },
            data={
                "total_calls": {
                    "increment": 1
                },
                "total_automated": {
                    "increment": 1
                }
            }
        )
    elif call_type == "transferred":
        await db.callstats.update(
            where={
                'user_id': user_id,
            },
            data={
                "total_calls": {
                    "increment": 1
                },
                "total_transferred": {
                    "increment": 1
                }
            }
        )
    elif call_type == "abandoned":
        await db.callstats.update(
            where={
                'user_id': user_id,
            },
            data={
                "total_calls": {
                    "increment": 1
                },
                "total_abandoned": {
                    "increment": 1
                }
            }
        )

    existing_call_logs = await db.call_logs.find_first(where={"user_id": user_id})

    if existing_call_logs is None:
        call_data = json.dumps([], separators=(',', ':'))
        await db.call_logs.create({
            "id": 1,
            "user_id": user_id,
            "call_data": Json(call_data),
        })
        print(f"Created new call log for user - {user_id} - dubious")

    else:
        new_call_data = [call_type, call_intent, datetime.datetime.now().isoformat()]

        old_call_data = json.loads(existing_call_logs.call_data)
        old_call_data.append(new_call_data)
        
        updated_call_data = json.dumps(old_call_data)

        await db.call_logs.update(
            where={
                'user_id': user_id,
            },
            data={
                "call_data": Json(updated_call_data)
            }
        )