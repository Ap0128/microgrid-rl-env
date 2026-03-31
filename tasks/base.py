from dataclasses import dataclass
from typing import Optional

@dataclass
class TaskConfig:
    task_id: str
    description: str
    difficulty: str
    solar_capacity_kw: float
    battery_capacity_kwh: float
    max_charge_kw: float
    load_mean_kw: float
    flex_fraction: float
    price_mean: float
    price_sigma: float
    price_spike_prob: float
    price_spike_min: float
    price_spike_max: float
    solar_sigma: float
    grid_outage_start: Optional[int]   # step index or None
    grid_outage_end: Optional[int]
    total_steps: int = 96

    def summary(self):
        return {
            "task_id": self.task_id,
            "difficulty": self.difficulty,
            "description": self.description,
            "total_steps": self.total_steps,
            "battery_capacity_kwh": self.battery_capacity_kwh,
        }