from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv
from typing import Optional

# --- NOVAS IMPORTAÇÕES ---
from pydantic import BaseModel, EmailStr

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET")

# Criptografia da senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Config JWT
SECRET_KEY = JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Para extrair token do header Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


# --- NOVO SCHEMA ---
# Define um schema para os dados que esperamos dentro do token
class TokenData(BaseModel):
    id: str   # O ID do usuário (vindo do 'sub')
    email: EmailStr # O email do usuário (vindo do 'email')
    name: str 
    image: Optional[str] = None


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=60))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- FUNÇÃO ATUALIZADA ---
# Função para validar token e retornar os dados do usuário (ID e Email)
def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extraímos os dois campos que colocamos no token
        user_id: str = payload.get("sub")
        user_email: str = payload.get("email")
        user_name: str = payload.get("name")
        user_image: str = payload.get("image", None)

        # Verificamos se ambos existem
        if user_id is None or user_email is None or user_name is None:
            raise credentials_exception
        
        # Validamos os dados usando o schema Pydantic
        token_data = TokenData(id=user_id, email=user_email, name=user_name, image=user_image)

    except JWTError:
        raise credentials_exception
    except Exception as e: # Captura erros de validação do Pydantic (ex: email inválido)
        raise credentials_exception

    # Retorna o objeto TokenData validado
    return token_data