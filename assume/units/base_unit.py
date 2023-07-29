from collections import defaultdict
from datetime import datetime
from typing import NamedTuple

import pandas as pd

# from assume.strategies.base_strategy import BaseStrategy


class BaseUnit:
    """A base class for a unit.

    Attributes
    ----------
    id : str
        The ID of the unit.
    technology : str
        The technology of the unit.
    node : str
        The node of the unit.

    Methods
    -------
    """

    def __init__(
        self,
        id: str,
        unit_operator: str,
        technology: str,
        bidding_strategies: dict,
        index: pd.DatetimeIndex,
        node: str,
    ):
        self.id = id
        self.unit_operator = unit_operator
        self.technology = technology
        self.node = node
        self.bidding_strategies: dict[str, "BaseStrategy"] = bidding_strategies
        self.index = index
        self.outputs = defaultdict(lambda: pd.Series(0.0, index=self.index))

    def reset(self):
        """Reset the unit to its initial state."""
        raise NotImplementedError()

    def calculate_bids(
        self,
        market_config,
        product_tuples: list[tuple],
        data_dict=None,
    ) -> list:
        """Calculate the bids for the next time step."""

        if market_config.product_type not in self.bidding_strategies:
            return []

        return self.bidding_strategies[market_config.product_type].calculate_bids(
            unit=self,
            market_config=market_config,
            product_tuples=product_tuples,
            data_dict=data_dict,
        )

    def set_dispatch_plan(
        self,
        dispatch_plan: dict,
        clearing_price: float,
        start: pd.Timestamp,
        end: pd.Timestamp,
        product_type: str,
    ):
        """
        adds dispatch plan from current market result to total dispatch plan
        """
        end_excl = end - self.index.freq
        self.outputs[product_type].loc[start:end_excl] += dispatch_plan["total_power"]

        self.calculate_cashflow(start=start, end=end, clearing_price=clearing_price)

        self.bidding_strategies[product_type].calculate_reward(
            start=start,
            end=end,
            product_type=product_type,
            clearing_price=clearing_price,
            unit=self,
        )

    def execute_current_dispatch(
        self,
        start: pd.Timestamp,
        end: pd.Timestamp,
    ):
        """
        check if the total dispatch plan is feasible
        This checks if the market feedback is feasible for the given unit.
        And sets the closest dispatch if not.
        The end param should be inclusive.
        """
        end_excl = end - self.index.freq
        return self.outputs["energy"][start:end_excl]

    def get_output_before(self, datetime: datetime, product_type: str = "energy"):
        if datetime - self.index.freq < self.index[0]:
            return 0
        else:
            return self.outputs["energy"].at[datetime - self.index.freq]

    def as_dict(self) -> dict:
        return {
            "technology": self.technology,
            "unit_operator": self.unit_operator,
            "unit_type": "base_unit",
        }

    def calculate_cashflow(
        self,
        start,
        end,
        clearing_price,
    ):
        pass


class SupportsMinMax(BaseUnit):
    """
    Base Class used for Powerplant derived classes
    """

    min_power: float
    max_power: float

    def calculate_min_max_power(
        self, start: pd.Timestamp, end: pd.Timestamp, product_type="energy"
    ) -> tuple[float]:
        pass

    def calculate_marginal_cost(self, start: pd.Timestamp, power: float) -> float:
        pass


class SupportsMinMaxCharge(BaseUnit):
    """
    Base Class used for Storage derived classes
    """

    min_power_charge: float
    max_power_charge: float
    min_power_discharge: float
    max_power_discharge: float

    def calculate_min_max_charge(
        self, start: pd.Timestamp, end: pd.Timestamp
    ) -> tuple[float]:
        pass

    def calculate_min_max_discharge(
        self, start: pd.Timestamp, end: pd.Timestamp
    ) -> tuple[float]:
        pass

    def calculate_marginal_cost(self, start: pd.Timestamp, power: float) -> float:
        pass
