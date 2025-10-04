from pydantic import BaseModel, field_validator, Field
from typing import Any
import re


class LoginModel(BaseModel):
    user_id: str
    password: str

    @field_validator("user_id")
    @classmethod
    def ensure_correct_format(cls, value: Any):
        invalid_user_id_msg = "Invalid User ID. Please use a dash (-). Example: 1234-4567"
        user_id_pattern = re.compile('^\d{4}-\d{4}$')

        if not user_id_pattern.match(value):
            raise ValueError(invalid_user_id_msg)

        return value
