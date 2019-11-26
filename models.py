from typing import Dict, List

from pydantic import BaseModel, ValidationError, create_model

Inf = float("inf")


class Tier(BaseModel):
    tier: float = Inf
    price: float = 0.0


RateKey = str


# You can create models out of non-Object types
class Rate(BaseModel):
    __root__: List[Tier]


class Plan(BaseModel):
    # using ellipses is just another way of writing `base: Rate`
    # showing that it is required
    # this supposedly does not play well with mypy so avoid it
    base: Rate = ...

    # this field is also required because we only use type annotation
    # and no default value
    usage: Dict[RateKey, Rate]

    class Config:
        # immutability support for base elements
        # one cannot change `base` but may change the contents of `base`
        allow_mutation = False


# https://home.tokyo-gas.co.jp/power/ryokin/menu_waribiki/menu1.html
plan = Plan(
    base=Rate(
        __root__=[
            Tier(tier=30, price=858),
            Tier(tier=40, price=1144),
            Tier(tier=50, price=1430),
            Tier(tier=60, price=1716),
        ]
    ),
    usage={
        # example of using parse_obj instead of setting __root__ explicitly
        "flat": Rate.parse_obj(
            [
                Tier(tier=140, price=23.67),
                Tier(tier=350, price=23.88),
                Tier(tier=Inf, price=26.41),
            ]
        )
    },
)


# try:
#     plan.base = Rate.parse_obj([Tier(tier=Inf, price=0.0)])
# except TypeError as e:
#     print(e)
"""
"Plan" is immutable and does not support item assignment
"""


################
# Dynamic Model
################

fields = {"foo": (str, None), "bar": (int, 123), "biz": (float, 0.19)}

fields__whitelist = ["foo", "bar"]

# field definitions should either be a tuple of (<type>, <default>)
# or just a default value
field_definitions = {
    key: (type_, default)
    for key, (type_, default) in fields.items()
    if key in fields__whitelist
}

DynamicModel = create_model("DynamicModel", **field_definitions)

# ...same as writing
# DynamicModel = create_model("DynamicModel", foo=(str, None), bar=(int, None))

# print(DynamicModel(foo="hello", bar=123))
"""
foo='hello' bar=123
"""

# try:
#     DynamicModel(foo=[1, 2, 3])
# except ValidationError as e:
#     print(str(e))
"""
1 validation error for DynamicModel
foo
  str type expected (type=type_error.str)
"""
