import asyncio
import datetime
import json
from prisma import Prisma

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

    # call_data = [call_type, call_intent, datetime.datetime.now().isoformat()]
    # call_logs = await db.call_logs.find_first(where={"user_id": user_id})

    # if call_logs is None:
    #     binary_data = json.dumps(call_data)
    #     await db,call_logs.create(
    #         user_id=user_id,
    #         call_data=binary_data
    #     )
    #     return
    
    # call_data = json.loads(call_logs["call_data"]) + call_data

    # await db.call_logs.update(
    #     where={
    #         'user_id': user_id,
    #     },
    #     data={
    #         "call_data": json.dumps(call_data)
    #     }
    # )


async def execute_task():
    await db.connect()
    await track_metrics("kp_1071d97754b44202a1cc766e2cc6a512", "automated", "Order Status")
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(execute_task())