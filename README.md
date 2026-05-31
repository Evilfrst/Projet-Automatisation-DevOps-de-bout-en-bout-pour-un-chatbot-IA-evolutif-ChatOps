<img width="1254" height="1254" alt="ChatGPT Image 31 mai 2026, 14_34_50" src="https://github.com/user-attachments/assets/02efea0b-2fa6-449e-9a78-538d157ef2ee" />

# 🚀 ChatOps AI — DevSecOps Automation Platform

![ChatOps Banner](https://github.com/user-attachments/assets/22c58201-4b21-4e16-a552-0167dd5c7891)

## 📖 Présentation

ChatOps AI Enterprise est une plateforme DevSecOps complète permettant de déployer, superviser et faire évoluer un chatbot IA dans un environnement proche de la production.

Le projet combine :

- Frontend moderne en Next.js
- API backend FastAPI
- Intégration OpenAI
- Conteneurisation Docker
- Orchestration Docker Compose
- CI/CD GitHub Actions
- Déploiement AWS EC2
- Infrastructure as Code avec Terraform
- Monitoring avec Prometheus, Grafana, Loki et Promtail
- Observabilité et métriques applicatives

---

## 🎯 Objectifs

- Automatiser le cycle de vie applicatif
- Déployer rapidement une solution IA en production
- Mettre en œuvre des pratiques DevOps et DevSecOps modernes
- Superviser les performances et la disponibilité des services
- Fournir une architecture évolutive et maintenable

---

## 🏗️ Architecture

```text
Utilisateur
     │
     ▼
┌──────────────┐
│ Frontend     │
│ Next.js      │
└──────┬───────┘
       │ HTTP
       ▼
┌──────────────┐
│ Backend      │
│ FastAPI      │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ OpenAI API   │
└──────────────┘

Monitoring
┌──────────────┐
│ Prometheus   │
│ Grafana      │
│ Loki         │
│ Promtail     │
└──────────────┘

CI/CD
GitHub → GitHub Actions → AWS EC2
```

---

## 🧱 Stack Technique

### Frontend
- Next.js 16
- React 19
- TypeScript
- Tailwind CSS
- Axios
- Framer Motion
- Recharts

### Backend
- Python 3.11+
- FastAPI
- Pydantic
- OpenAI SDK
- Prometheus Instrumentator

### DevOps
- Docker
- Docker Compose
- GitHub Actions

### Cloud
- AWS EC2
- AWS VPC
- AWS Security Groups

### Monitoring
- Prometheus
- Grafana
- Loki
- Promtail

### Infrastructure as Code
- Terraform

---

## 📂 Structure du Projet

```text
.
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
│
├── backend/
│   ├── app/
│   │   └── main.py
│   ├── requirements.txt
│   └── dockerfile
│
├── frontend/
│   ├── app/
│   ├── public/
│   ├── package.json
│   └── dockerfile
│
├── monitoring/
│   ├── prometheus.yml
│   ├── alerts.yml
│   ├── alertmanager.yml
│   └── grafana-dashboard.json
│
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── provider.tf
│
├── k8s/
│   ├── backend-deployment.yaml
│   ├── frontend-deployment.yaml
│   └── service.yaml
│
├── tests/
├── docker-compose.yml
└── README.md
```

---

## ⚙️ Fonctionnalités

### Frontend
- Interface chatbot moderne
- Dashboard de supervision
- Responsive Design
- Communication temps réel avec l’API

### Backend
- Endpoint de chat IA
- Endpoint Health Check
- Gestion des erreurs
- Journalisation centralisée
- Instrumentation Prometheus

### DevOps
- Construction automatique des images Docker
- Déploiement automatisé sur AWS
- Gestion des secrets GitHub
- Infrastructure reproductible

### Monitoring
- Collecte des métriques
- Dashboards Grafana
- Centralisation des logs
- Alerting Prometheus

---

## 🔌 API

### Vérification de santé

```http
GET /health
```

Réponse :

```json
{
  "status": "healthy"
}
```

### Informations du service

```http
GET /
```

Réponse :

```json
{
  "status": "online",
  "service": "ChatOps AI Enterprise",
  "version": "2.0.0"
}
```

### Chat IA

```http
POST /chat
```

Corps :

```json
{
  "prompt": "Explique Docker"
}
```

Réponse :

```json
{
  "response": "Docker est une plateforme..."
}
```

---

## 🐳 Déploiement Local

### Cloner le projet

```bash
git clone <repository-url>
cd chatops-ai
```

### Variables d’environnement

Créer un fichier `.env` :

```env
OPENAI_API_KEY=your_api_key
ENVIRONMENT=development
PORT=8000
```

### Lancer avec Docker Compose

```bash
docker compose up -d --build
```

Services :

| Service | URL |
|----------|-----|
| Frontend | http://IP_AWS:3000 |
| Backend | http://IP_AWS:8000 |
| Prometheus | http://IP_AWS:9090 |
| Grafana | http://IP_AWS:3001 |

---

## ☁️ Déploiement AWS

L’infrastructure Terraform crée notamment :

- VPC dédié
- Sous-réseau public
- Internet Gateway
- Table de routage
- Security Group
- Instance EC2

### Terraform

```bash
cd terraform

terraform init
terraform plan
terraform apply
```

---

## 🔄 Pipeline CI/CD

### CI

À chaque push :

1. Checkout du code
2. Installation des dépendances
3. Exécution des tests
4. Build Docker

### CD

Après validation :

1. Copie des fichiers vers EC2
2. Connexion SSH
3. Reconstruction des conteneurs
4. Redémarrage de la stack

---

## 🔐 Sécurité

Bonnes pratiques intégrées :

- Secrets GitHub Actions
- Variables d’environnement
- Isolation des conteneurs
- Infrastructure versionnée
- Automatisation des déploiements

Améliorations possibles :

- Authentification JWT
- Reverse Proxy Nginx
- HTTPS avec Let's Encrypt
- Scan SAST/DAST
- Gestion des secrets AWS Secrets Manager

---

## 📊 Observabilité

### Prometheus

Collecte :
- Disponibilité API
- Temps de réponse
- Nombre de requêtes
- Erreurs applicatives

### Grafana

Visualisation :
- Santé des services
- Consommation ressources
- Trafic API
- Logs centralisés

---

## 🧪 Tests

Lancement :

```bash
pytest -v
```

---

## 🚀 Évolutions Futures

- Authentification utilisateur
- Historique des conversations
- Base de données PostgreSQL
- Kubernetes complet
- Helm Charts
- GitOps avec ArgoCD
- Multi-environnements Dev / Staging / Prod
- Intégration LLM locale
- RAG et vector database

---

## 👨‍💻 Auteur

Projet réalisé dans le cadre d’une démonstration complète DevOps / DevSecOps appliquée à un chatbot IA moderne.

## 📄 Licence

Projet distribué à des fins pédagogiques et démonstratives.


