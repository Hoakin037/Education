from pydantic import EmailStr, BaseModel, Field

class UserBase(BaseModel):
    email: str = Field(max_length=255)

class UserUpdateInfo(UserBase):
    new_email: str | None = Field(default=None, max_length=255)
    fullname: str | None = Field(default=None, max_length=255)
    name: str | None = Field(default=None, max_length=255)

class UpdatePassword(UserBase):
    email: str = Field(max_length=255)
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)

class UserRegister(UserBase):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(max_length=30)
    fullname: str | None = Field(max_length=255, default=None)
