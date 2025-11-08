from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from .. import schemas, models, auth
from ..database import get_db
import os
import shutil
from datetime import datetime

UPLOAD_DIR = "app/uploads"
UPLOAD_DIR_RELATIVE = "uploads"

router = APIRouter(prefix="/infracoes", tags=["infracoes"])
@router.get("/consultar", response_model=schemas.InfractionsResponse)
def consultar_infracoes(
    placa: str,
    db: Session = Depends(get_db),
    current_email: str = Depends(auth.get_current_user)
):
    veiculo = db.query(models.Car).filter(models.Car.placa_numero == placa).first()

    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")

    infracoes = db.query(models.Infraction).filter(models.Infraction.veiculo_id == veiculo.id).all()

    if not infracoes:
        raise HTTPException(status_code=404, detail="Nenhuma infração encontrada para esta placa")

    return {"placa": veiculo.placa_numero, "infracoes": infracoes}