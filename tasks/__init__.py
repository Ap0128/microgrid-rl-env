from tasks.base import TaskConfig
from tasks.sunny_day import SUNNY_DAY
from tasks.volatile_market import VOLATILE_MARKET
from tasks.islanded_crisis import ISLANDED_CRISIS

TASKS = {
    "sunny_day": SUNNY_DAY,
    "volatile_market": VOLATILE_MARKET,
    "islanded_crisis": ISLANDED_CRISIS,
}

def load_task(task_id: str) -> TaskConfig:
    if task_id not in TASKS:
        raise ValueError(f"Unknown task_id: '{task_id}'. Choose from: {list(TASKS.keys())}")
    return TASKS[task_id]
