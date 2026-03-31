import numpy as np
from tasks.base import TaskConfig


def generate_solar(rng: np.random.RandomState, config: TaskConfig) -> np.ndarray:
    """Sine-curve solar with Gaussian noise. Peak at midday (step 48)."""
    t = np.arange(config.total_steps)
    base = np.maximum(0, np.sin(np.pi * t / config.total_steps))
    noise = rng.normal(1.0, config.solar_sigma, size=config.total_steps)
    noise = np.clip(noise, 0.0, 2.0)
    solar = base * config.solar_capacity_kw * noise
    return np.clip(solar, 0.0, config.solar_capacity_kw)


def generate_load(rng: np.random.RandomState, config: TaskConfig) -> np.ndarray:
    """Double-hump load curve: morning peak ~step 28, evening peak ~step 72."""
    t = np.arange(config.total_steps)
    morning = np.exp(-0.5 * ((t - 28) / 10) ** 2)
    evening = np.exp(-0.5 * ((t - 72) / 10) ** 2)
    base = config.load_mean_kw * (0.6 + 0.6 * morning + 0.7 * evening)
    noise = rng.normal(0, 0.05 * config.load_mean_kw, size=config.total_steps)
    return np.clip(base + noise, config.load_mean_kw * 0.3, config.load_mean_kw * 2.0)


def generate_prices(rng: np.random.RandomState, config: TaskConfig) -> np.ndarray:
    """AR(1) mean-reverting price with occasional spikes."""
    prices = np.zeros(config.total_steps)
    rho = 0.85
    prices[0] = config.price_mean

    for t in range(1, config.total_steps):
        ar_component = rho * prices[t - 1] + (1 - rho) * config.price_mean
        noise = rng.normal(0, config.price_sigma)
        spike = 0.0
        if config.price_spike_prob > 0 and rng.random() < config.price_spike_prob:
            spike = rng.uniform(config.price_spike_min, config.price_spike_max)
        prices[t] = max(0.01, ar_component + noise + spike)

    return prices


def generate_grid_availability(config: TaskConfig) -> np.ndarray:
    """Deterministic grid availability. False during outage window."""
    availability = np.ones(config.total_steps, dtype=bool)
    if config.grid_outage_start is not None and config.grid_outage_end is not None:
        availability[config.grid_outage_start:config.grid_outage_end] = False
    return availability


def update_soc(soc: float, requested_kw: float, config: TaskConfig, dt: float = 0.25):
    """
    Apply battery action. Returns (new_soc, actual_kw_delivered).
    Positive kw = charging. Efficiency applied correctly.
    """
    cap = config.battery_capacity_kwh
    max_kw = config.max_charge_kw

    # Clamp to physical limits
    requested_kw = np.clip(requested_kw, -max_kw, max_kw)

    if requested_kw >= 0:
        # Charging: efficiency reduces energy stored
        energy_stored = requested_kw * dt * 0.95
        new_soc = soc + energy_stored / cap
    else:
        # Discharging: efficiency reduces energy delivered
        energy_drawn = abs(requested_kw) * dt / 0.95
        new_soc = soc - energy_drawn / cap

    # Hard clamp SoC to [0, 1]
    new_soc = float(np.clip(new_soc, 0.0, 1.0))
    actual_kw = (new_soc - soc) * cap / dt  # back-calculate actual kW
    return new_soc, actual_kw