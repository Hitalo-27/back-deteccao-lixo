from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from .. import schemas, models, auth
from ..database import get_db
from datetime import datetime
from typing import List
import os
import requests

UPLOAD_DIR = "app/uploads"
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
MODEL_ID = "trash-wecic/1"

# Diretório para salvar uploads temporariamente
os.makedirs(UPLOAD_DIR, exist_ok=True)


router = APIRouter(prefix="/lixo", tags=["lixo"])
@router.get("/consultar", response_model=List[schemas.LixoResponse])
def consultar_lixo(
    user: int,
    # current_email: str = Depends(auth.get_current_user),
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


@router.post("/detectar")
async def detectar_lixo(
    filename: str = Body(..., embed=True),  # agora vem no body JSON
    db: Session = Depends(get_db),
    current_email: str = Depends(auth.get_current_user)
):
    """
    Detecta lixo em uma imagem existente no diretório de uploads.
    """

    # Monta o caminho completo
    file_path = os.path.join(UPLOAD_DIR, filename)

    # Verifica se o arquivo existe
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Arquivo {filename} não encontrado em {UPLOAD_DIR}")

    try:
        # Envia para o Roboflow
        with open(file_path, "rb") as img:
            response = requests.post(
                f"https://detect.roboflow.com/{MODEL_ID}?api_key={ROBOFLOW_API_KEY}",
                files={"file": img},
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Erro Roboflow: {response.text}"
            )

        result = response.json()

        return {
            "status": "ok",
            "arquivo": file_path,
            "resultado": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar imagem: {e}")