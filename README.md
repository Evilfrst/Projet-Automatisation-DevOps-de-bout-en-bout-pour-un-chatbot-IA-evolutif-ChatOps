# ChatOps AI - DevOps Automation Project
<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/0826abe9-55b7-414b-bd72-86675220c4f0" />

Projet DevOps complet et industrialisé pour un chatbot IA avec :
- FastAPI
- Docker
- Docker Compose
- GitHub Actions CI/CD
- Tests automatisés
- Linting
- Monitoring Prometheus
- Healthchecks
- Sécurité basique
- Déploiement prêt pour production

## Lancement local

```bash
docker compose up --build
```

API :
http://localhost:8000/docs

## Pipeline CI/CD

Le workflow GitHub Actions :
- installe les dépendances
- lance les tests
- lance le lint
- construit l'image Docker
- vérifie le health endpoint

## Structure

```
.
├── app/
├── tests/
├── monitoring/
├── .github/workflows/
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```
## Features Added

- Modern AI SaaS frontend
- OpenAI integration
- FastAPI AI backend
- Prometheus metrics
- Grafana monitoring
- Docker Compose enterprise stack
- DevOps dashboard
- AI chat system

## Start Project

### Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

### Frontend
cd frontend
npm install
npm run dev

### Full Stack
docker compose up -d

## URLs

Frontend:
http://localhost:3000

Backend:
http://localhost:8000

Prometheus:
http://localhost:9090

Grafana:
http://localhost:3001

## Grafana Credentials

admin
admin

