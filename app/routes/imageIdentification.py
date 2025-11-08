from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from geopy.geocoders import Nominatim
import os

router = APIRouter(prefix="/image", tags=["veiculos"])

# Caminho base onde as imagens estão salvas
IMAGE_DIR = "app/images"  # ajuste conforme seu projeto


def get_exif_data(image):
    """Extrai todos os metadados EXIF da imagem."""
    exif_data = {}
    info = getattr(image, "_getexif", lambda: None)()
    if not info:
        return {}

    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        if decoded == "GPSInfo":
            gps_data = {}
            for t in value:
                sub_decoded = GPSTAGS.get(t, t)
                gps_data[sub_decoded] = value[t]
            exif_data["GPSInfo"] = gps_data
        else:
            exif_data[decoded] = value
    return exif_data


def rational_to_float(r):
    """Converte valores IFDRational, tuplas ou números em float."""
    try:
        if hasattr(r, "numerator") and hasattr(r, "denominator"):
            return float(r.numerator) / float(r.denominator)
        elif isinstance(r, (tuple, list)) and len(r) == 2:
            return float(r[0]) / float(r[1])
        elif isinstance(r, (int, float)):
            return float(r)
        return float(r)
    except Exception:
        return None


def convert_to_degrees(value):
    """Converte coordenadas EXIF (possivelmente IFDRational) em graus decimais."""
    try:
        d, m, s = [rational_to_float(v) for v in value]
        if None in (d, m, s):
            return None
        return d + (m / 60.0) + (s / 3600.0)
    except Exception:
        return None


def clean_exif_data(data):
    """Converte e limpa o EXIF inteiro para tipos serializáveis e legíveis."""
    if isinstance(data, dict):
        return {str(k): clean_exif_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_exif_data(i) for i in data]
    elif hasattr(data, "numerator") and hasattr(data, "denominator"):
        return rational_to_float(data)
    elif isinstance(data, bytes):
        # Decodifica bytes e remove caracteres nulos (\x00)
        return data.decode(errors="ignore").replace("\x00", "").strip()
    elif isinstance(data, str):
        # Remove caracteres invisíveis (\x00, etc)
        return data.replace("\x00", "").strip()
    else:
        try:
            return float(data)
        except Exception:
            try:
                return str(data).replace("\x00", "").strip()
            except Exception:
                return None


def parse_address(raw_address):
    """Tenta separar o endereço retornado pelo Nominatim em partes estruturadas."""
    if not raw_address:
        return None

    addr = {
        "rua": None,
        "numero": None,
        "cidade": None,
        "estado": None,
        "pais": None,
        "cep": None,
    }

    try:
        # Alguns locais retornam dict detalhado em 'raw'
        address_data = raw_address.raw.get("address", {})
        addr["rua"] = address_data.get("road") or address_data.get("pedestrian") or address_data.get("footway")
        addr["numero"] = address_data.get("house_number")
        addr["cidade"] = address_data.get("city") or address_data.get("town") or address_data.get("village")
        addr["estado"] = address_data.get("state_code") or address_data.get("state")
        addr["pais"] = address_data.get("country")
        addr["cep"] = address_data.get("postcode")

        # Corrige sigla da UF (ex: "São Paulo" → "SP")
        uf_map = {
            "Acre": "AC", "Alagoas": "AL", "Amapá": "AP", "Amazonas": "AM", "Bahia": "BA",
            "Ceará": "CE", "Distrito Federal": "DF", "Espírito Santo": "ES", "Goiás": "GO",
            "Maranhão": "MA", "Mato Grosso": "MT", "Mato Grosso do Sul": "MS", "Minas Gerais": "MG",
            "Pará": "PA", "Paraíba": "PB", "Paraná": "PR", "Pernambuco": "PE", "Piauí": "PI",
            "Rio de Janeiro": "RJ", "Rio Grande do Norte": "RN", "Rio Grande do Sul": "RS",
            "Rondônia": "RO", "Roraima": "RR", "Santa Catarina": "SC", "São Paulo": "SP",
            "Sergipe": "SE", "Tocantins": "TO",
        }

        if addr["estado"] in uf_map:
            addr["estado"] = uf_map[addr["estado"]]

    except Exception:
        pass

    return addr


@router.post("/identification")
async def get_metadata(data: dict = Body(...)):
    try:
        filename = data.get("filename")
        if not filename:
            return JSONResponse(
                status_code=400,
                content={"erro": "Campo 'filename' é obrigatório no corpo da requisição."},
            )

        image_path = os.path.join(IMAGE_DIR, filename)
        if not os.path.exists(image_path):
            return JSONResponse(
                status_code=404,
                content={"erro": f"Arquivo '{filename}' não encontrado em {IMAGE_DIR}"},
            )

        img = Image.open(image_path)
        exif = get_exif_data(img)
        exif_clean = clean_exif_data(exif)

        gps_info = exif.get("GPSInfo", {})
        location = None
        address_data = None
        debug = {}

        if gps_info:
            lat_raw = gps_info.get("GPSLatitude")
            lon_raw = gps_info.get("GPSLongitude")
            lat_ref = gps_info.get("GPSLatitudeRef")
            lon_ref = gps_info.get("GPSLongitudeRef")

            if lat_raw and lon_raw:
                lat = convert_to_degrees(lat_raw)
                lon = convert_to_degrees(lon_raw)

                if lat_ref == "S":
                    lat = -lat
                if lon_ref == "W":
                    lon = -lon

                location = {"latitude": lat, "longitude": lon}

                if lat and lon:
                    try:
                        geolocator = Nominatim(user_agent="metadata_extractor")
                        loc = geolocator.reverse((lat, lon), language="pt")
                        if loc:
                            address_data = parse_address(loc)
                    except Exception as e:
                        debug["geopy_error"] = str(e)

        return {
            "arquivo": filename,
            "gps": location,
            "local": address_data,
            "metadados": exif_clean,
            "debug": debug,
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"erro": "Erro ao processar imagem", "detalhes": str(e)},
        )
