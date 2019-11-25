import pickle
from pathlib import Path
from tempfile import gettempdir

from models import Inf, Plan

plan_dict = {
    "base": [
        {"tier": 30.0, "price": 858.0},
        {"tier": 40.0, "price": 1144.0},
        {"tier": 50.0, "price": 1430.0},
        {"tier": 60.0, "price": 1716.0},
    ],
    "usage": {
        "flat": [
            {"tier": 140.0, "price": 23.67},
            {"tier": 350.0, "price": 23.88},
            {"tier": Inf, "price": 26.41},
        ]
    },
}

tmp = Path(gettempdir()) / "pydantic-playground.pkl"

with open(tmp, "wb") as f:
    pickle.dump(plan_dict, f)

# https://pydantic-docs.helpmanual.io/usage/models/#helper-functions
plan = Plan.parse_file(tmp, content_type="application/pickle", allow_pickle=True)
print(plan.json())
"""
{
    "base": [
        {"tier": 30.0, "price": 858.0},
        {"tier": 40.0, "price": 1144.0},
        {"tier": 50.0, "price": 1430.0},
        {"tier": 60.0, "price": 1716.0}
    ],
    "usage": {
        "flat": [
            {"tier": 140.0, "price": 23.67},
            {"tier": 350.0, "price": 23.88},
            {"tier": Infinity, "price": 26.41}
        ]
    }
}
"""


print(Plan.parse_obj(plan_dict))
"""
base=[
    Tier(tier=30.0, price=858.0),
    Tier(tier=40.0, price=1144.0),
    Tier(tier=50.0, price=1430.0),
    Tier(tier=60.0, price=1716.0)
]
usage={
    'flat': [
        Tier(tier=140.0, price=23.67),
        Tier(tier=350.0, price=23.88),
        Tier(tier=inf, price=26.41)
    ]
}
"""
