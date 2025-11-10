from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    image_url = Column(String, nullable=True)

class Lixo(Base):
    __tablename__ = "lixo"

    id = Column(Integer, primary_key=True, index=True)
    data = Column(DateTime, nullable=False)
    imagem = Column(String(255), nullable=False)
    latitude = Column(String(20), nullable=True)
    longitude = Column(String(20), nullable=True)
    rua = Column(String(255), nullable=True)
    numero = Column(Integer, nullable=True)
    cidade = Column(String(100), nullable=True)
    estado = Column(String(2), nullable=True)
    pais = Column(String(50), nullable=True)
    cep = Column(String(9), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User")