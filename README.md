<img width="1254" height="1254" alt="ChatGPT Image 31 mai 2026, 14_34_50" src="https://github.com/user-attachments/assets/02efea0b-2fa6-449e-9a78-538d157ef2ee" />

# 🚀 ChatOps AI — DevSecOps Automation Platform

![ChatOps Banner](https://github.com/user-attachments/assets/22c58201-4b21-4e16-a552-0167dd5c7891)

📌 Présentation

ChatOps AI Enterprise est une plateforme DevOps intelligente intégrant un chatbot IA basé sur OpenAI, une architecture cloud moderne et une chaîne d'automatisation complète.

Le projet démontre une approche DevOps de bout en bout incluant :

Développement Backend avec FastAPI
Interface Frontend moderne avec Next.js
Base de données PostgreSQL
Conteneurisation Docker
Intégration Continue (CI) avec GitHub Actions
Déploiement Continu (CD)
Monitoring avec Prometheus et Grafana
Collecte des logs avec Loki et Promtail
Infrastructure as Code avec Terraform
Orchestration Kubernetes
🏗 Architecture
Utilisateur
      │
      ▼
Frontend Next.js
      │
      ▼
Backend FastAPI
      │
 ┌────┴────┐
 ▼         ▼
OpenAI   PostgreSQL
 API
      │
      ▼
Prometheus
      │
      ▼
Grafana
      │
      ▼
Loki + Promtail
📂 Structure du projet
.
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   └── init_db.py
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   ├── public/
│   ├── package.json
│   └── tsconfig.json
│
├── monitoring/
│   ├── prometheus.yml
│   ├── alerts.yml
│   ├── alertmanager.yml
│   └── grafana-dashboard.json
│
├── terraform/
│   ├── provider.tf
│   ├── main.tf
│   ├── outputs.tf
│   └── variables.tf
│
├── k8s/
│   ├── backend-deployment.yaml
│   ├── frontend-deployment.yaml
│   └── service.yaml
│
├── tests/
│   └── test_api.py
│
├── docker-compose.yml
├── docker-compose.monitoring.yml
└── README.md
🛠 Technologies utilisées
Backend
Python 3.11
FastAPI
SQLAlchemy
PostgreSQL
OpenAI SDK
Frontend
Next.js
React
TypeScript
TailwindCSS
DevOps
Docker
Docker Compose
GitHub Actions
Terraform
Kubernetes
Monitoring
Prometheus
Grafana
Loki
Promtail
Node Exporter
⚙️ Variables d'environnement

Créer un fichier .env :

OPENAI_API_KEY=your_openai_api_key

DATABASE_URL=postgresql://chatops:chatops123@postgres:5432/chatops
🚀 Lancement local
1. Cloner le dépôt
git clone <repository-url>
cd ChatOps-AI-Enterprise
2. Démarrer l'ensemble de la plateforme
docker compose up -d --build
3. Vérifier les conteneurs
docker ps
🌐 Accès aux services
Service	URL
Frontend	http://localhost:3000
Backend API	http://localhost:8000
Swagger	http://localhost:8000/docs
Prometheus	http://localhost:9090
Grafana	http://localhost:3001
Alertmanager	http://localhost:9093
Node Exporter	http://localhost:9100/metrics
📊 Monitoring
Prometheus

Vérification :

curl http://localhost:8000/metrics
Grafana

Connexion :

Utilisateur : admin
Mot de passe : admin

Importer :

monitoring/grafana-dashboard.json
Loki

Ajouter une datasource Loki :

URL:
http://loki:3100

Tester avec :

{job="docker"}
🗄 PostgreSQL

Connexion :

docker exec -it postgres psql -U chatops -d chatops

Lister les tables :

\dt

Afficher les conversations :

SELECT * FROM conversations;
🤖 API Chatbot
Envoyer une question
POST /chat

Body :

{
  "prompt": "Comment déployer Kubernetes ?"
}

Réponse :

{
  "response": "..."
}
Historique
GET /history

Réponse :

[
  {
    "id": 1,
    "user_message": "...",
    "ai_response": "..."
  }
]
🧪 Tests

Exécuter :

pytest -v

Tests disponibles :

Endpoint /
Endpoint /health
Endpoint /chat
🔄 Pipeline CI/CD

GitHub Actions exécute automatiquement :

Installation des dépendances
Lint
Tests Pytest
Build Frontend
Build Docker
Déploiement
☸️ Déploiement Kubernetes

Appliquer :

kubectl apply -f k8s/

Vérifier :

kubectl get pods
kubectl get svc
🏗 Infrastructure Terraform

Initialisation :

terraform init

Plan :

terraform plan

Déploiement :

terraform apply
🔒 Sécurité
Variables sensibles dans .env
Secrets GitHub Actions
Isolation Docker
Monitoring des métriques
Journalisation centralisée
📈 Fonctionnalités

✅ Chatbot IA OpenAI

✅ Historique des conversations

✅ PostgreSQL

✅ Docker Compose

✅ Monitoring Prometheus

✅ Dashboard Grafana

✅ Logs Loki

✅ Terraform

✅ Kubernetes

✅ GitHub Actions

👨‍💻 Auteur

Projet réalisé dans le cadre d'un projet DevOps complet démontrant l'automatisation d'une plateforme IA moderne.

ChatOps AI Enterprise


