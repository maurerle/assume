from assume.common.market_objects import market_mechanism

from .all_or_nothing import pay_as_bid_aon, pay_as_clear_aon
from .base import pay_as_bid, pay_as_clear
from .pyomo_clearing import nodal_pricing_pyomo
from .complex_clearing import pay_as_clear_opt

clearing_mechanisms: dict[str, market_mechanism] = {
    "pay_as_clear": pay_as_clear,
    "pay_as_bid": pay_as_bid,
    "pay_as_bid_all_or_nothing": pay_as_bid_aon,
    "pay_as_clear_all_or_nothing": pay_as_clear_aon,
    "nodal_pricing_pyomo": nodal_pricing_pyomo,
    "pay_as_clear_opt": pay_as_clear_opt,
}
