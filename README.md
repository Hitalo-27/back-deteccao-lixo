# 🚀 Backend Completo - EcoDetect (FastAPI + MySQL)

Este é o **backend completo** do projeto desenvolvido em **Python** utilizando **FastAPI**.  
Ele fornece uma **API REST** para todas as funcionalidades do sistema.
---

## 📌 Tecnologias utilizadas
- Python 3.13+
- FastAPI
- MySQL
- SQLAlchemy
- Passlib (hash de senhas)
- Python-JOSE (JWT)

---

## ⚙️ Como rodar localmente

1. Clone o repositório:
```bash
git clone <URL_DO_REPOSITORIO>
cd <NOME_DA_PASTA_CLONADA>
```

2. Crie o banco de dados MySQL com o arquivo `ecodetect.sql`.

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute a aplicação:
```bash
uvicorn app.main:app --reload
```

## ⚙️ Todos os endpoints
A documentação interativa da API está disponível em:
👉 ```http://127.0.0.1:8000/docs```