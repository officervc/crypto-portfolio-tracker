from pydantic import BaseModel, EmailStr, field_validator
@field_validator("password")
@classmethod
def validate_password(cls, v):
    if len(v) < 8:
        raise ValueError("Password must be at least 8 characters")
    if len(v) > 72:
        raise ValueError("Password cannot be longer than 72 characters")
    if not any(c.isupper() for c in v):
        raise ValueError("Password must contain at least one uppercase letter")
    if not any(c.isdigit() for c in v):
        raise ValueError("Password must contain at least one number")
    return v   
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

    #@field_validator("password")
    #@classmethod
    #def validate_password(cls, v):
     #   if len(v) < 8:
      #      raise ValueError("Password must be at least 8 characters")
       # if not any(c.isupper() for c in v):
        #    raise ValueError("Password must contain at least one uppercase letter")
        #if not any(c.isdigit() for c in v):
         #   raise ValueError("Password must contain at least one number")
        #return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"