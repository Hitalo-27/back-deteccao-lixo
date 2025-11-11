import os
import cv2
import requests
from fastapi import HTTPException

UPLOAD_DIR = "app/uploads"
DETECTED_DIR = "app/detect"
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
MODEL_ID = "lixo-com-impacto-ambiental/1"

def detectar_lixo(filename: str):
    """
    Detecta lixo em uma imagem existente no diretório de uploads.
    Retorna o resultado da detecção e o caminho da imagem processada.
    """

    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Arquivo {filename} não encontrado em {UPLOAD_DIR}")

    try:
        # === 1️⃣ Envia imagem para Roboflow ===
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

        # === 2️⃣ Carrega imagem original ===
        imagem = cv2.imread(file_path)

        # === 3️⃣ Pós-processamento ===
        detections_validas = 0
        for pred in predictions:
            conf = pred.get("confidence", 0)
            if conf < 0.30:
                continue
            detections_validas += 1

            x, y = pred["x"], pred["y"]
            w, h = pred["width"], pred["height"]
            x1, y1 = int(x - w / 2), int(y - h / 2)
            x2, y2 = int(x + w / 2), int(y + h / 2)

            cv2.rectangle(imagem, (x1, y1), (x2, y2), (0, 255, 0), 3)
            texto = f"{pred['class']} ({conf * 100:.1f}%)"
            cv2.putText(imagem, texto, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # === 4️⃣ Salvar imagem detectada ===
        detected_filename = f"detected_{os.path.basename(filename)}"
        detected_path = os.path.join(DETECTED_DIR, detected_filename)
        os.makedirs(DETECTED_DIR, exist_ok=True)
        cv2.imwrite(detected_path, imagem)

        return {
            "detections_validas": detections_validas,
            "arquivo_original": file_path,
            "arquivo_processado": detected_path,
            "resultado": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar imagem: {e}")
