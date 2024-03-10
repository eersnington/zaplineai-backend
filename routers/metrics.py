# Import necessary modules
from fastapi import APIRouter
from datetime import datetime, timedelta
from pydantic import BaseModel
import sqlite3

from lib.auth import check_user
from lib.custom_exception import CustomException

# Create a router instance
router = APIRouter(prefix="/metrics")

conn = sqlite3.connect('user_metrics.db')
c = conn.cursor()


class UserMetrics(BaseModel):
    user_id: str
    calls: int
    automated_calls: int
    transferred_calls: int
    abandoned_calls: int


class MetricsForm(BaseModel):
    user_id: str


def safe_division(numerator, denominator):
    if denominator == 0:
        return 0
    return numerator / denominator


def add_metrics(form: UserMetrics) -> dict:
    """
        Adds user metrics to the database.
    """
    sql = '''INSERT INTO user_metrics (user_id, calls, automated_calls, transferred_calls, abandoned_calls)
             VALUES (?, ?, ?, ?, ?)'''
    data = (form.user_id, form.calls, form.automated_calls,
            form.transferred_calls, form.abandoned_calls)

    try:
        with conn:
            c.execute(sql, data)
        conn.commit()

    except sqlite3.Error as e:
        raise CustomException(f"Database error: {e}", 500)
    except Exception as e:
        raise CustomException(f"An error occurred: {e}", 500)


def total_metrics(form: MetricsForm) -> tuple:
    """
        Returns the total metrics for a user.
    """
    try:
        c.execute('''SELECT SUM(calls), SUM(automated_calls), SUM(transferred_calls), SUM(abandoned_calls) FROM user_metrics WHERE user_id=?''', (form.user_id,))
        total_metrics = c.fetchone()
        if total_metrics[0] is None:
            return (0, 0, 0, 0)
        else:
            return total_metrics

    except sqlite3.Error as e:
        raise CustomException(f"Database error: {e}", 500)
    except Exception as e:
        raise CustomException(f"An error occurred: {e}", 500)


def weekly_metrics(form: MetricsForm) -> dict:
    """
        Returns the metrics for a user over the past week.
    """
    weekly_metrics = {}
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        date_str = date.strftime("%b %d, %Y")
        # Query to get metrics for each day
        c.execute('''SELECT SUM(calls), SUM(automated_calls), SUM(transferred_calls) FROM user_metrics WHERE user_id=? AND DATE(timestamp) = ?''',
                  (form.user_id, date.strftime("%Y-%m-%d")))
        metrics = c.fetchone()
        if metrics[0] is not None:
            weekly_metrics[date_str] = {
                "total_calls": metrics[0],
                "automated_calls": metrics[1],
                "transferred_calls": metrics[2]
            }
        else:
            weekly_metrics[date_str] = {
                "total_calls": 0,
                "automated_calls": 0,
                "transferred_calls": 0
            }
    return weekly_metrics


def recent_metrics(form: MetricsForm) -> list:
    """
        Returns a list of tuples containing most recent 7 calls for a given user.
    """
    c.execute('''SELECT strftime('%Y-%m-%d %H:%M:%S', timestamp), call_type, call_intent FROM user_metrics WHERE user_id=? ORDER BY timestamp DESC LIMIT 7''', (form.user_id,))
    recent_calls = c.fetchall()

    if len(recent_calls) == 0:
        return [("No recent calls", "N/A", "N/A")]
    return recent_calls


@router.get("/")
async def root(form: MetricsForm):
    await check_user(form.user_id)

    week = recent_metrics(form)
    return {"result": week}


@router.get("/get")
async def get_user_metrics(form: MetricsForm):
    await check_user(form.user_id)

    tm = total_metrics(form)

    automated_call_rate = safe_division(tm[1], tm[0]) * 100
    transferred_call_rate = safe_division(tm[2], tm[0]) * 100
    abandoned_call_rate = safe_division(tm[3], tm[0]) * 100

    wm = weekly_metrics(form)
    rm = recent_metrics(form)

    # Construct a JSON response
    return {
        "total_metrics": {
            "total_calls": tm[0],
            "total_automated_calls": tm[1],
            "automated_call_rate": f"{automated_call_rate:.2f}%",
            "total_transferred_calls": tm[2],
            "transferred_call_rate": f"{transferred_call_rate:.2f}%",
            "total_abandoned_calls": tm[3],
            "abandoned_call_rate": f"{abandoned_call_rate:.2f}%"
        },
        "weekly_metrics": wm,
        "recent_metrics": rm
    }
