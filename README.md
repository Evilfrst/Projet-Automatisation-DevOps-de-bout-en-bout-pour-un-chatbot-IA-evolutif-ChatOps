<img width="1254" height="1254" alt="ChatGPT Image 31 mai 2026, 14_34_50" src="https://github.com/user-attachments/assets/02efea0b-2fa6-449e-9a78-538d157ef2ee" />

# 🚀 ChatOps AI — DevSecOps Automation Platform

![ChatOps Banner](https://github.com/user-attachments/assets/22c58201-4b21-4e16-a552-0167dd5c7891)

📖 Présentation

ChatOps AI Enterprise est une plateforme cloud-native permettant aux utilisateurs d'interagir avec une Intelligence Artificielle via une interface web moderne tout en mettant en œuvre les bonnes pratiques DevOps, DevSecOps et SRE.

Ce projet a été conçu pour démontrer la maîtrise de :

Cloud Computing
Infrastructure as Code
CI/CD
Monitoring & Alerting
Containerisation
Kubernetes
Observabilité
Automatisation
Intégration IA
🎯 Objectifs du projet

L'objectif principal est de construire une plateforme de production capable de :

✅ Interroger une IA générative

✅ Être déployée automatiquement

✅ Être supervisée en temps réel

✅ Déclencher des alertes automatiques

✅ Être scalable et maintenable

✅ Respecter les pratiques DevOps modernes

🏗️ Architecture
                     +----------------+
                     |   Utilisateur  |
                     +--------+-------+
                              |
                              v
                   +-------------------+
                   |   Frontend Next.js |
                   +---------+----------+
                             |
                             v
                   +-------------------+
                   | Backend FastAPI   |
                   +---------+----------+
                             |
                             v
                   +-------------------+
                   |    OpenAI API     |
                   +-------------------+

──────────────────────────────────────────

Monitoring

Prometheus
     |
Grafana
     |
Alertmanager
     |
Email Alerts

──────────────────────────────────────────

CI/CD

GitHub Actions
      |
Docker Build
      |
AWS Deployment

──────────────────────────────────────────

Infrastructure

Terraform
     |
AWS EC2

──────────────────────────────────────────

Containerisation

Docker
Docker Compose
Kubernetes
🛠️ Stack Technique
Frontend
Next.js
React
TypeScript
Tailwind CSS
Backend
Python
FastAPI
OpenAI SDK
Cloud
AWS EC2
Infrastructure as Code
Terraform
Containerisation
Docker
Docker Compose
Orchestration
Kubernetes
CI/CD
GitHub Actions
Monitoring
Prometheus
Grafana
Alertmanager
📂 Structure du Projet
chatops-ai/

├── frontend/
│   ├── app/
│   ├── public/
│   └── Dockerfile
│
├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
│
├── monitoring/
│   ├── prometheus.yml
│   ├── alerts.yml
│   ├── alertmanager.yml
│   └── grafana/
│
├── terraform/
│
├── kubernetes/
│
├── .github/
│   └── workflows/
│
└── docker-compose.yml
⚙️ Fonctionnalités
IA Conversationnelle
Questions / réponses IA
Interface temps réel
Gestion des requêtes utilisateur
Monitoring
Disponibilité des services
Consommation CPU
Consommation mémoire
Temps de réponse API
Alerting
Backend indisponible
Forte charge CPU
Forte consommation mémoire
Latence excessive
Dashboard
Grafana
Visualisation temps réel
KPI système
🚀 Déploiement Local
Cloner le dépôt
git clone https://github.com/username/chatops-ai.git

cd chatops-ai
Variables d'environnement

Créer :

backend/.env
OPENAI_API_KEY=your_api_key
Lancer les services
docker compose up -d
Vérification

Frontend :

http://IP_AWS:3000

Backend :

http://IP_AWS:8000/docs

Grafana :

http://IP_AWS:3001

Prometheus :

http://IP_AWS:9090

Alertmanager :

http://IP_AWS:9093
☁️ Déploiement AWS

Provisionnement automatique :

cd terraform

terraform init

terraform plan

terraform apply

Création :

EC2
Security Groups
Réseau
🔄 CI/CD

Pipeline GitHub Actions :

Push
 ↓
Tests
 ↓
Build Docker
 ↓
Push Images
 ↓
Déploiement AWS
 ↓
Redémarrage Services

Déclenchement automatique à chaque commit.

📊 Observabilité
Prometheus

Collecte :

Disponibilité
Temps de réponse
Métriques applicatives
Grafana

Visualisation :

CPU
RAM
Requêtes
État du backend
Alertmanager

Notifications automatiques :

Email
Alertes critiques
Résolution automatique
📧 Alertes

Exemple :

[ChatOps AI] BackendDown

Service : FastAPI

Niveau : Critical

Description :
Le backend est indisponible depuis plus d'une minute.
🔒 Sécurité
Gestion sécurisée des secrets
Variables d'environnement
Isolation Docker
Contrôle des accès AWS
Security Groups
🧪 Tests
Backend
pytest
Docker
docker compose ps
Monitoring
curl IP_AWS:8000/metrics
📈 Compétences démontrées
Cloud Engineering
DevOps
DevSecOps
SRE
Infrastructure as Code
CI/CD
Monitoring
Alerting
Containerisation
Kubernetes
Automatisation
Intelligence Artificielle
📷 Démonstration
Dashboard
KPI système
Monitoring temps réel
Observabilité
Chatbot
Interaction IA
Réponses génératives
Alertes
Détection automatique
Notification e-mail
👨‍💻 Auteur

Projet réalisé dans le cadre d'une démonstration complète des pratiques DevOps, Cloud Engineering et Observabilité appliquées à une plateforme IA moderne.

📜 Licence

Projet pédagogique et démonstratif.


