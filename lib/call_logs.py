import json
import os
from datetime import datetime
from typing import Optional

def get_call_logs(user_id: str) -> Optional[list]:
    """
    Retrieve call logs for a given user ID.

    Args:
    - user_id (str): The user ID for which to retrieve call logs.

    Returns:
    - list or None: A list containing the call logs if found, or None if no logs are found for the user.
    """
    logs_folder = f"./call_logs/{user_id}"
    if os.path.exists(logs_folder):
        logs = []
        for filename in os.listdir(logs_folder):
            file_path = os.path.join(logs_folder, filename)
            with open(file_path, "r") as file:
                log = json.load(file)
            logs.append(log)
        return logs
    else:
        return None

def store_call_log(user_id: str, call_id: str, transcript: list):
    """
    Store a call log entry for a given user ID.

    Args:
    - user_id (str): The user ID for which to store the call log.
    - call_id (str): The unique identifier for the call.
    - transcript (list): The transcript of the call.
    """
    logs_folder = f"./call_logs/{user_id}"
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    log = {
        "call_id": call_id,
        "timestamp": timestamp,
        "transcript": transcript
    }
    file_path = os.path.join(logs_folder, f"{timestamp}.json")
    with open(file_path, "w") as file:
        json.dump(log, file)

if __name__ == "__main__":
    user_id = "123456"
    call_id = "789"
    transcript = ["Test", "Test2"]
    store_call_log(user_id, call_id, transcript)
    fetched = get_call_logs(user_id=user_id)
    if fetched:
        print(fetched)
