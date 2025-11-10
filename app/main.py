from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routes import imageIdentification
from .database import Base, engine
from .routes import users
from .routes import lixo

# Criar tabelas no banco
Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Backend em Python")

# Configurar CORS para permitir o frontend Next.js (localhost:3000)
origins = [
    "*",  # endereço do seu frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # pode usar ["*"] para liberar todos os domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rotas
app.include_router(users.router)
app.include_router(lixo.router)
app.include_router(imageIdentification.router)

@app.get("/")
def root():
    return {"msg": "API rodando com sucesso 🚀"}

# Serve a pasta uploads como /uploads
app.mount("/uploads", StaticFiles(directory="app/uploads"), name="uploads")

app.mount("/detect", StaticFiles(directory="app/detect"), name="detect")
