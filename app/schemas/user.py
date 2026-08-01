from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    age: int


class UserUpdate(BaseModel):
    name: str | None = None
    age: int | None = None


class UserResponse(BaseModel):
    id: int
    name: str
    age: int

    model_config = {"from_attributes": True}
