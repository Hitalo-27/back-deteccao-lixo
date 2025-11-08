from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from .. import schemas, models, auth
from ..database import get_db
import os
import shutil
from datetime import datetime


UPLOAD_DIR = "app/uploads"
UPLOAD_DIR_RELATIVE = "uploads"

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    hashed_password = auth.hash_password(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not auth.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token = auth.create_access_token({"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserResponse)
def get_me(
    current_email: str = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == current_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

@router.put("/update")
async def update_user(
    username: str = Form(None),
    email: str = Form(None),
    old_password: str = Form(None),
    new_password: str = Form(None),
    new_password_confirm: str = Form(None),
    image: UploadFile = File(None),  # Novo campo
    current_email: str = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == current_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Atualiza username
    if username:
        user.username = username

    # Atualiza email
    if email:
        existing_user = db.query(models.User).filter(models.User.email == email).first()
        if existing_user and existing_user.id != user.id:
            raise HTTPException(status_code=400, detail="Email já cadastrado")
        user.email = email

    # Atualiza senha
    if old_password or new_password or new_password_confirm:
        if not (old_password and new_password and new_password_confirm):
            raise HTTPException(status_code=400, detail="Preencha todas as senhas para alterar")
        if not auth.verify_password(old_password, user.password):
            raise HTTPException(status_code=400, detail="Senha antiga incorreta")
        if new_password != new_password_confirm:
            raise HTTPException(status_code=400, detail="Novas senhas não conferem")
        user.password = auth.hash_password(new_password)

    # Salvar imagem (se enviada)
    if image:
        # Garante que a pasta exista
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Cria nome único (ex: user_5_20251007_2120.png)
        ext = os.path.splitext(image.filename)[1]
        new_filename = f"user_{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        file_path = os.path.join(UPLOAD_DIR, new_filename)

        # Salva o arquivo
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Atualiza campo no banco
        user.image_url = f"/{UPLOAD_DIR_RELATIVE}/{new_filename}"

    db.commit()
    db.refresh(user)

    return {"message": "Usuário atualizado com sucesso", "image_url": user.image_url if image else None}