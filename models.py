from typing import Dict, List

from pydantic import BaseModel, ValidationError

Inf = float("inf")


class Tier(BaseModel):
    tier: float = Inf
    price: float = 0.0


Rate = List[Tier]
RateKey = str


class Plan(BaseModel):
    base: Rate
    usage: Dict[RateKey, Rate]


# https://home.tokyo-gas.co.jp/power/ryokin/menu_waribiki/menu1.html
plan = Plan(
    base=[
        Tier(tier=30, price=858),
        Tier(tier=40, price=1144),
        Tier(tier=50, price=1430),
        Tier(tier=60, price=1716),
    ],
    usage={
        "flat": [
            Tier(tier=140, price=23.67),
            Tier(tier=350, price=23.88),
            Tier(tier=Inf, price=26.41),
        ]
    },
)
