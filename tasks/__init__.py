from tasks.base import TaskConfig

TASKS = {

    "sunny_day": TaskConfig(
        task_id="sunny_day",
        description="Stable solar generation and demand",
        difficulty="easy",
        solar_capacity_kw=40,
        battery_capacity_kwh=100,
        max_charge_kw=10,
        load_mean_kw=25,
        flex_fraction=0.2,
        price_mean=80,
        price_sigma=10,
        price_spike_prob=0.0,
        price_spike_min=0,
        price_spike_max=0,
        solar_sigma=0.05,
        grid_outage_start=None,
        grid_outage_end=None,
    ),

    "volatile_market": TaskConfig(
        task_id="volatile_market",
        description="Highly volatile electricity prices",
        difficulty="medium",
        solar_capacity_kw=40,
        battery_capacity_kwh=100,
        max_charge_kw=10,
        load_mean_kw=25,
        flex_fraction=0.25,
        price_mean=90,
        price_sigma=40,
        price_spike_prob=0.15,
        price_spike_min=200,
        price_spike_max=400,
        solar_sigma=0.10,
        grid_outage_start=None,
        grid_outage_end=None,
    ),

    "islanded_crisis": TaskConfig(
        task_id="islanded_crisis",
        description="Grid outage scenario with tight constraints",
        difficulty="hard",
        solar_capacity_kw=35,
        battery_capacity_kwh=80,
        max_charge_kw=8,
        load_mean_kw=30,
        flex_fraction=0.15,
        price_mean=120,
        price_sigma=30,
        price_spike_prob=0.3,
        price_spike_min=250,
        price_spike_max=500,
        solar_sigma=0.15,
        grid_outage_start=30,
        grid_outage_end=70,
    ),
}


def load_task(task_id: str) -> TaskConfig:
    if task_id not in TASKS:
        raise ValueError(f"Unknown task: {task_id}")
    return TASKS[task_id]
