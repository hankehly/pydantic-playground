from typing import Dict, List

from pydantic import BaseModel, confloat, conlist, constr, create_model

Inf = float("inf")

StrictPositiveFloat = confloat(strict=True, gt=0)
"""
Can also be written as below, but pycharm type hints show warning

class StrictPositiveFloat(ConstrainedFloat):
    gt = 0
    strict = True
"""

NonNegativeFloat = confloat(ge=0)


class Tier(BaseModel):
    tier: StrictPositiveFloat = Inf
    price: NonNegativeFloat = 0.0


RateKey = constr(strip_whitespace=True, min_length=1, regex="^[a-z_]+$", strict=True)
"""
Can also be written:

class RateKey(ConstrainedStr):
    strip_whitespace = True
    min_length = 1
    regex = re.compile("^[a-z_]+$")
    strict = True
"""


# You can create models out of non-Object types
class Rate(BaseModel):
    __root__: conlist(Tier, min_items=1)


class Plan(BaseModel):
    base: Rate = Rate.parse_obj([Tier()])

    # this field required because we only use type annotation
    # and no default value
    usage: Dict[RateKey, Rate]

    class Config:
        # immutability support for base elements
        # one cannot change `base` but may change the contents of `base`
        allow_mutation = False


# https://home.tokyo-gas.co.jp/power/ryokin/menu_waribiki/menu1.html
plan = Plan(
    base=Rate.parse_obj(
        [
            Tier(tier=30.0, price=858.0),
            Tier(tier=40.0, price=1144.0),
            Tier(tier=50.0, price=1430.0),
            Tier(tier=60.0, price=1716.0),
        ]
    ),
    usage={
        # example of using parse_obj instead of setting __root__ explicitly
        "flat": Rate.parse_obj(
            [
                Tier(tier=140.0, price=23.67),
                Tier(tier=350.0, price=23.88),
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
