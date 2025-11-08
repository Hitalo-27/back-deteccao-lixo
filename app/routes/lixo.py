from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, models, auth
from ..database import get_db
from datetime import datetime
from typing import List

UPLOAD_DIR = "app/uploads"
UPLOAD_DIR_RELATIVE = "uploads"

router = APIRouter(prefix="/lixo", tags=["lixo"])
@router.get("/consultar", response_model=List[schemas.LixoResponse])
def consultar_lixo(
    user: int,
    current_email: str = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    
    lixo = db.query(models.Lixo).filter(models.Lixo.user_id == user).all()

    if not lixo:
        raise HTTPException(status_code=404, detail="Nenhum lixo encontrado")

    return lixo

@router.post("/registrar", response_model=schemas.LixoBase)
def registrar_lixo(
    lixo: schemas.LixoBase,
    current_user: str = Depends(auth.get_current_user),  # autenticação opcional
    db: Session = Depends(get_db),
):
    # Verifica se o usuário existe
    user = db.query(models.User).filter(models.User.id == lixo.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Verifica se o endereço existe
    endereco = db.query(models.Address).filter(models.Address.id == lixo.endereco_id).first()
    if not endereco:
        raise HTTPException(status_code=404, detail="Endereço não encontrado")

    # Cria novo registro de lixo
    novo_lixo = models.Lixo(
        data=lixo.data,
        imagem=lixo.imagem,
        latitude=lixo.latitude,
        longitude=lixo.longitude,
        user_id=lixo.user_id,
        endereco_id=lixo.endereco_id
    )

    # Salva no banco
    db.add(novo_lixo)
    db.commit()
    db.refresh(novo_lixo)

    return novo_lixo
