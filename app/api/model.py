from pydantic import EmailStr, Field, BaseModel
from re import match
import uuid

ACCESS_TOKEN_EXPIRE_MINUTES = 60          
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  

class ValidationError(Exception): 
            """Raises when password is not valid."""

class UserBase(BaseModel):
    email: EmailStr = Field(max_length=255)
    full_name: str | None = Field(default=None, max_length=255)

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)

    def validate_pass(self):
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$'
        

        if match(pattern, self.password) is None:
            raise ValidationError('Пароль слишком простой!')

class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  
    password: str | None = Field(default=None, min_length=8, max_length=128)

class UserInDB(UserBase):
    hashed_password: str
    username: str
    disabled: bool = False

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    payload: dict

class SignUp(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str | None = None
    full_name: str | None = None
    password: str = Field(..., min_length=8)

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "username": "alice",
                "email": "alice@example.com",
                "full_name": "Alice Wonder",
                "password": "supersecret123"
            }]
        }
    }

class SignUpResp(BaseModel):
    username: str
    email: str | None
    full_name: str | None
    disabled: bool = False