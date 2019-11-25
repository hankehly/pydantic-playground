from models import Plan
from pydantic import BaseModel, ValidationError, validator, PydanticValueError

try:
    Plan()
except ValidationError as e:
    print("JSON representation")
    print("-------------------")
    print(e.json(), end="\n\n")

    print("Python representation")
    print("---------------------")
    print(e.errors(), end="\n\n")

    print("Human readable")
    print("--------------")
    print(str(e))
"""
JSON representation
-------------------
[
  {
    "loc": [
      "base"
    ],
    "msg": "field required",
    "type": "value_error.missing"
  },
  {
    "loc": [
      "usage"
    ],
    "msg": "field required",
    "type": "value_error.missing"
  }
]

Python representation
---------------------
[
    {
        'loc': ('base',),
        'msg': 'field required',
        'type': 'value_error.missing'
    }, 
    {
        'loc': ('usage',), 
        'msg': 'field required', 
        'type': 'value_error.missing'
    }
]

Human readable
--------------
2 validation errors for Plan
base
  field required (type=value_error.missing)
usage
  field required (type=value_error.missing)
"""


class CustomValidationModel(BaseModel):
    name: str

    @validator("name")
    def name_must_be_foo(cls, value):
        if value != "foo":
            raise ValueError(f"name must be foo, got {value}")
        return value


try:
    CustomValidationModel(name="bar")
except ValidationError as e:
    print(e.errors())
"""
[
    {
        'loc': ('name',),
        'msg': 'name must be foo, got bar',
        'type': 'value_error'
    }
]
"""


class CustomErrorType(PydanticValueError):
    code = "custom_error_type"
    msg_template = "This is a custom error message. Received bad value: {bad_value}"


class CustomValidationModel2(BaseModel):
    name: str

    @validator("name")
    def name_must_be_foo(cls, value):
        if value != "foo":
            raise CustomErrorType(bad_value=value)
        return value


try:
    CustomValidationModel2(name="bar")
except ValidationError as e:
    print(e.errors())
"""
[
    {
        'loc': ('name',),
        'msg': 'This is a custom error message. Received bad value: bar',
        'type': 'value_error.custom_error_type',
        'ctx': {'bad_value': 'bar'}
    }
]
"""
