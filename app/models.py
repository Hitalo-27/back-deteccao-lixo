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

    veiculos = relationship("Car", back_populates="endereco")