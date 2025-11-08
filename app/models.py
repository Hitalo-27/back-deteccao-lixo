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

class Address(Base):
    __tablename__ = "endereco"

    id = Column(Integer, primary_key=True, index=True)
    pais = Column(String(45), index=True, nullable=False)
    estado = Column(String(80), index=True, nullable=False)
    cidade = Column(String(80), index=True, nullable=False)

class Lixo(Base):
    __tablename__ = "lixo"

    id = Column(Integer, primary_key=True, index=True)
    data = Column(DateTime, nullable=False)
    imagem = Column(String(255), nullable=False)
    latitude = Column(String(20), nullable=True)
    longitude = Column(String(20), nullable=True)
    endereco_id = Column(Integer, ForeignKey("endereco.id"), nullable=False)
    endereco = relationship("Address") 
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User")