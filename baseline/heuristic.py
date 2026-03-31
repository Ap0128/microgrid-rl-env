from env.models import MicrogridState, MicrogridAction
from tasks.base import TaskConfig


class ThresholdHeuristicBaseline:

    def act(self, state: MicrogridState, config: TaskConfig) -> MicrogridAction:
        action, _ = self.act_with_reason(state, config)
        return action

    def act_with_reason(self, state: MicrogridState, config: TaskConfig):
        soc = state.soc
        solar = state.solar_kw
        base_load = state.base_load_kw
        flex_load = state.flexible_load_kw
        price = state.spot_price
        max_kw = config.max_charge_kw

        # Rule 1: Emergency — SoC critically low
        if soc < 0.12:
            return (
                MicrogridAction(battery_kw=max_kw * 0.5, curtail_fraction=0.9),
                "Rule 1: Emergency SoC. Charging and curtailing."
            )

        # Rule 2: Grid outage — conserve
        if not state.grid_available:
            curtail = 0.9 if soc < 0.30 else 0.6
            discharge = min(base_load - solar, max_kw * 0.6)
            discharge = max(0.0, discharge)
            return (
                MicrogridAction(battery_kw=-discharge, curtail_fraction=curtail),
                f"Rule 2: Islanded. Discharging {discharge:.1f}kW, curtail={curtail}"
            )

        # Rule 3: Solar surplus — charge battery
        total_load = base_load + flex_load
        surplus = solar - total_load
        if surplus > 2.0 and soc < 0.85:
            charge = min(surplus, max_kw)
            return (
                MicrogridAction(battery_kw=charge, curtail_fraction=0.0),
                f"Rule 3: Solar surplus {surplus:.1f}kW. Charging at {charge:.1f}kW."
            )

        # Rule 4: Price spike — discharge
        spike_threshold = config.price_mean * 2.0
        if price > spike_threshold and soc > 0.30:
            discharge = min(base_load, max_kw * 0.8)
            return (
                MicrogridAction(battery_kw=-discharge, curtail_fraction=0.4),
                f"Rule 4: Price spike ${price:.3f}. Discharging {discharge:.1f}kW."
            )

        # Rule 5: Cheap grid — opportunistic charge
        if price < config.price_mean * 0.8 and soc < 0.50:
            return (
                MicrogridAction(battery_kw=max_kw * 0.4, curtail_fraction=0.0),
                "Rule 5: Low price. Charging from grid."
            )

        # Rule 6: Evening — gentle discharge
        if state.step > 64 and solar < 5.0 and soc > 0.35:
            return (
                MicrogridAction(battery_kw=-max_kw * 0.3, curtail_fraction=0.2),
                "Rule 6: Evening discharge."
            )

        # Default
        return (
            MicrogridAction(battery_kw=0.0, curtail_fraction=0.0),
            "Default: No action."
        )