from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional
from typing import List

# Para entrada (cadastro)
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# Para resposta
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    image_url: Optional[str] = None

    class Config:
        from_attributes = True

# Para login
class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    old_password: Optional[str] = None
    new_password: Optional[str] = None
    new_password_confirm: Optional[str] = None

class AddressBase(BaseModel):
    pais: str
    estado: str
    cidade: str

class LixoBase(BaseModel):
    data: datetime
    imagem: str
    latitude: str
    longitude: str
    endereco_id: int
    user_id: int

class LixoResponse(BaseModel):
    data: datetime
    imagem: str
    latitude: str
    longitude: str
    endereco: AddressBase
    user: UserResponse
    class Config:
        from_attributes = True