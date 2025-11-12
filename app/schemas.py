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
    
class LixoBase(BaseModel):
    data: Optional[datetime] = None
    imagem: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    rua: Optional[str] = None
    numero: Optional[int] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    pais: Optional[str] = None
    cep: Optional[str] = None
    user_id: Optional[int] = None

class LixoResponse(BaseModel):
    data: Optional[datetime] = None
    imagem: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    rua: Optional[str] = None
    numero: Optional[int] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    pais: Optional[str] = None
    cep: Optional[str] = None
    user: UserResponse
    class Config:
        from_attributes = True