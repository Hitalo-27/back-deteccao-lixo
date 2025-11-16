import os
import cv2
import requests
from fastapi import HTTPException

UPLOAD_DIR = "app/uploads"
DETECTED_DIR = "app/detect"
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
MODEL_ID = "lixo-com-impacto-ambiental/1"

def compactar_imagem(path: str, max_width=1920, qualidade=80):
    """Compacta e redimensiona a imagem automaticamente."""
    try:
        image = cv2.imread(path)

        if image is None:
            raise HTTPException(400, f"Erro ao abrir a imagem {path}")

        altura, largura = image.shape[:2]

        # Redimensiona se necessário
        if largura > max_width:
            escala = max_width / largura
            nova_largura = int(largura * escala)
            nova_altura = int(altura * escala)
            image = cv2.resize(image, (nova_largura, nova_altura))

        # Sempre salva como JPG para ficar leve
        compactado = path.replace(".png", ".jpg").replace(".jpeg", ".jpg")
        cv2.imwrite(compactado, image, [cv2.IMWRITE_JPEG_QUALITY, qualidade])

        return compactado

    except Exception as e:
        raise HTTPException(500, f"Erro ao compactar imagem: {e}")


def detectar_lixo(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(404, f"Arquivo {filename} não encontrado em {UPLOAD_DIR}")

    try:
        # === 0️⃣ Compacta automaticamente antes de enviar ===
        file_path_compactado = compactar_imagem(file_path)

        # === 1️⃣ Envia imagem compactada para Roboflow ===
        with open(file_path_compactado, "rb") as img:
            response = requests.post(
                f"https://detect.roboflow.com/{MODEL_ID}?api_key={ROBOFLOW_API_KEY}",
                files={"file": img},
            )

        if response.status_code != 200:
            raise HTTPException(response.status_code, response.text)

        result = response.json()
        predictions = result.get("predictions", [])

        # === 2️⃣ Carrega imagem compactada ===
        imagem = cv2.imread(file_path_compactado)
        if imagem is None:
            raise HTTPException(400, f"OpenCV não conseguiu abrir {file_path_compactado}")

        # === 3️⃣ Marcar detecções ===
        detections_validas = 0
        for pred in predictions:
            if pred.get("confidence", 0) < 0.30:
                continue

            detections_validas += 1

            x, y = pred["x"], pred["y"]
            w, h = pred["width"], pred["height"]
            x1, y1 = int(x - w / 2), int(y - h / 2)
            x2, y2 = int(x + w / 2), int(y + h / 2)

            cv2.rectangle(imagem, (x1, y1), (x2, y2), (0, 255, 0), 3)
            texto = f"{pred['class']} ({pred['confidence']*100:.1f}%)"
            cv2.putText(imagem, texto, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # === 4️⃣ Salvar detectada ===
        os.makedirs(DETECTED_DIR, exist_ok=True)
        detected_path = os.path.join(DETECTED_DIR, f"detected_{filename}")
        cv2.imwrite(detected_path, imagem)

        return {
            "detections_validas": detections_validas,
            "arquivo_original": file_path,
            "arquivo_processado": detected_path,
            "resultado": result
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(500, str(e))
