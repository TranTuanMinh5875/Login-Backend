from pydantic import BaseModel, EmailStr, validator

class Email(BaseModel):
    value: EmailStr
    
    @validator('value')
    def normalize_email(cls, v):
        return v.lower().strip()
    
    def __str__(self):
        return self.value