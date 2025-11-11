import shutil
from fastapi import APIRouter, Depends, HTTPException, Body, UploadFile, File
from sqlalchemy.orm import Session
from .. import schemas, models, auth
from ..database import get_db
from datetime import datetime
from typing import List
import os
import requests
from app.utils.image_metadata import extract_image_metadata
from app.utils.detectar_lixo import detectar_lixo

UPLOAD_DIR = "app/uploads"
UPLOAD_DIR_RELATIVE = "uploads"
UPLOAD_DIR_RELATIVE_DETECTED = "detect/detected_"
DETECTED_DIR = "app/detect"
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
MODEL_ID = "lixo-com-impacto-ambiental/1"

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

@router.post("/registrar")
async def registrar(
    image: UploadFile = File(...),
    current_email: str = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    # Busca usuário autenticado
    user = db.query(models.User).filter(models.User.email == current_email.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Cria diretório de upload se não existir
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Define nome único de arquivo
    ext = os.path.splitext(image.filename)[1]
    new_filename = f"lixo_{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
    file_path = os.path.join(UPLOAD_DIR, new_filename)

    # Salva imagem
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # Extrai metadados
    try:
        metadata = extract_image_metadata(new_filename, base_dir=UPLOAD_DIR)
    except Exception as e:
        metadata = {"erro": str(e)}

    gps = metadata.get("gps") or {}
    local = metadata.get("local", {}) or {}
    metadados = metadata.get("metadados", {})
    latitude = gps.get("latitude")
    longitude = gps.get("longitude")

    # === 🚀 Detectar lixo antes de salvar ===
    resultado = detectar_lixo(new_filename)

    if resultado["detections_validas"] == 0:
        # Nenhum lixo detectado → não salva no banco
        return {
            "success": 0,
            "message": "Nenhum lixo detectado na imagem.",
            "lixo": []
        }

    # === ✅ Salva no banco apenas se detectou ===
    novo_lixo = models.Lixo(
        data=metadados.get("DateTime"),
        imagem=f"/{UPLOAD_DIR_RELATIVE_DETECTED}{new_filename}",
        latitude=latitude,
        longitude=longitude,
        rua=local.get("rua"),
        numero=local.get("numero"),
        cidade=local.get("cidade"),
        estado=local.get("estado"),
        pais=local.get("pais"),
        cep=local.get("cep"),
        user_id=user.id,
    )

    db.add(novo_lixo)
    db.commit()
    db.refresh(novo_lixo)

    return {
        "success": 1,
        "message": "Lixo registrado com sucesso.",
        "lixo": novo_lixo,
    }

@router.post("/detectar")
async def detectar_lixo_API(
    filename: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_email: str = Depends(auth.get_current_user)
):
    """
    Detecta lixo em uma imagem existente no diretório de uploads.
    Faz o pós-processamento da resposta do Roboflow,
    desenhando as bounding boxes e aplicando filtros de confiança.
    """

    import os
    import cv2
    import requests
    from fastapi import HTTPException

    # Caminho completo da imagem
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Arquivo {filename} não encontrado em {UPLOAD_DIR}")

    try:
        # === 1️⃣ Envia a imagem para o Roboflow ===
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
        predictions = result.get("predictions", [])

        # === 2️⃣ Carrega a imagem original ===
        imagem = cv2.imread(file_path)

        # === 3️⃣ Lógica de pós-processamento ===
        if not predictions:
            return {
                "status": "ok",
                "arquivo": file_path,
                "mensagem": "🗑️ Lixo não detectado.",
                "resultado": result
            }

        detections_validas = 0

        for pred in predictions:
            conf = pred.get("confidence", 0)
            if conf < 0.30:
                continue  # ignorar falso positivo

            detections_validas += 1

            # Conversão das coordenadas (YOLO -> OpenCV)
            x, y = pred["x"], pred["y"]
            w, h = pred["width"], pred["height"]
            x1, y1 = int(x - w/2), int(y - h/2)
            x2, y2 = int(x + w/2), int(y + h/2)

            # Desenhar bounding box
            cv2.rectangle(imagem, (x1, y1), (x2, y2), (0, 255, 0), 3)
            texto = f"{pred['class']} ({conf*100:.1f}%)"
            cv2.putText(imagem, texto, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # === 4️⃣ Salvar imagem com detecção ===
        detected_filename = f"detected_{os.path.basename(filename)}"
        detected_path = os.path.join(DETECTED_DIR, detected_filename)
        cv2.imwrite(detected_path, imagem)

        # === 5️⃣ Retornar resultado final ===
        if detections_validas == 0:
            mensagem = "⚠️ Falso positivo (todas as detecções com baixa confiança)."
        else:
            mensagem = f"✅ {detections_validas} detecção(ões) válida(s) encontrada(s)."

        return {
            "status": "ok",
            "arquivo_original": file_path,
            "arquivo_processado": detected_path,
            "mensagem": mensagem,
            "resultado": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar imagem: {e}")
    
@router.post("/detectarOG")
async def detectar_lixo_API(
    filename: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_email: str = Depends(auth.get_current_user)
):
    """
    Detecta ou classifica o tipo de lixo em uma imagem existente no diretório de uploads.
    Compatível tanto com modelos de detecção (YOLO) quanto de classificação (sem bounding box).
    """

    import os
    import cv2
    import requests
    from fastapi import HTTPException

    # Caminho completo da imagem
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Arquivo {filename} não encontrado em {UPLOAD_DIR}")

    try:
        # === 1️⃣ Envia a imagem para o Roboflow ===
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
        predictions = result.get("predictions")

        # === 2️⃣ Verifica o tipo de saída ===
        # Caso 1: Modelo de DETECÇÃO (lista de bounding boxes)
        if isinstance(predictions, list):
            imagem = cv2.imread(file_path)

            if not predictions:
                return {
                    "status": "ok",
                    "arquivo": file_path,
                    "mensagem": "🗑️ Lixo não detectado.",
                    "resultado": result
                }

            detections_validas = 0
            for pred in predictions:
                conf = pred.get("confidence", 0)
                if conf < 0.30:
                    continue

                detections_validas += 1

                # Converte coordenadas YOLO → OpenCV
                x, y = pred["x"], pred["y"]
                w, h = pred["width"], pred["height"]
                x1, y1 = int(x - w/2), int(y - h/2)
                x2, y2 = int(x + w/2), int(y + h/2)

                # Desenhar bounding box
                cv2.rectangle(imagem, (x1, y1), (x2, y2), (0, 255, 0), 3)
                texto = f"{pred['class']} ({conf*100:.1f}%)"
                cv2.putText(imagem, texto, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # === Salva imagem detectada ===
            detected_filename = f"detected_{os.path.basename(filename)}"
            detected_path = os.path.join(UPLOAD_DIR, detected_filename)
            cv2.imwrite(detected_path, imagem)

            if detections_validas == 0:
                mensagem = "⚠️ Falso positivo (todas as detecções com baixa confiança)."
            else:
                mensagem = f"✅ {detections_validas} detecção(ões) válida(s) encontrada(s)."

            return {
                "status": "ok",
                "arquivo_original": file_path,
                "arquivo_processado": detected_path,
                "mensagem": mensagem,
                "resultado": result
            }

        # Caso 2: Modelo de CLASSIFICAÇÃO (dicionário de classes)
        elif isinstance(predictions, dict):
            imagem = cv2.imread(file_path)

            # Pega a classe com maior confiança
            classe_top = max(predictions.items(), key=lambda x: x[1]["confidence"])
            classe_nome, dados = classe_top
            conf = dados["confidence"]

            if conf < 0.30:
                mensagem = "⚠️ Falso positivo (confiança muito baixa)."
            else:
                mensagem = f"✅ Lixo ai ai ai aiai detectado: {classe_nome} ({conf*100:.1f}%)."

            # === Desenhar o texto sobre a imagem ===
            altura, largura, _ = imagem.shape
            texto = f"{classe_nome.upper()} ({conf*100:.1f}%)"

            # Fundo retangular preto atrás do texto
            cv2.rectangle(imagem, (0, 0), (largura, 60), (0, 0, 0), -1)
            # Escreve o texto
            cv2.putText(imagem, texto, (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

            # === Salva imagem com o texto ===
            detected_filename = f"detected_{os.path.basename(filename)}"
            detected_path = os.path.join(DETECTED_DIR, detected_filename)
            cv2.imwrite(detected_path, imagem)

            return {
                "status": "ok",
                "arquivo_original": file_path,
                "arquivo_processado": detected_path,
                "mensagem": mensagem,
                "classe_detectada": classe_nome if conf >= 0.30 else None,
                "confianca": conf,
                "resultado": result
            }

        # Caso 3: Tipo de resposta inesperado
        else:
            raise HTTPException(status_code=500, detail="Formato de resposta do Roboflow não reconhecido.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar imagem: {e}")