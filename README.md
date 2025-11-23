# ♻️ EcoDetect – Backend Completo (FastAPI + MySQL + YOLO + Roboflow)

Este repositório contém o backend completo do projeto EcoDetect, desenvolvido com Python e FastAPI.
Ele fornece uma API REST responsável por autenticação, processamento de imagens, detecção de lixo irregular e comunicação com o banco de dados.

Projeto desenvolvido para a APS de Sistemas Distribuídos do 8º semestre do curso de Ciência da Computação – UNIP.

O objetivo do EcoDetect é identificar lixo descartado em locais irregulares a partir de imagens enviadas pelos usuários.
As ocorrências detectadas podem ser encaminhadas às autoridades responsáveis, permitindo:

- Manter o meio ambiente limpo

- Acelerar a coleta de resíduos

- Aplicar penalidades quando necessário

- Reduzir o número de ocorrências ao longo do tempo

## 🛠️ Tecnologias Utilizadas

- Python 3.13+

- FastAPI (API REST)

- MySQL (banco de dados)

- SQLAlchemy (ORM)

- Passlib (hash de senhas)

- Python-JOSE (JWT para autenticação)

- YOLO – You Only Look Once (detecção de objetos)

- Roboflow (gerenciamento e treinamento do modelo YOLO)

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

## 📚 Documentação da API

A documentação interativa (Swagger) está disponível em:

👉 ```http://127.0.0.1:8000/docs```

## 🖥️ Frontend do Projeto

O frontend do EcoDetect está disponível no repositório:

👉 ```https://github.com/guilhermeAbbenante/APS-EcoDetect-FrontEnd```