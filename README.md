# 🚀 ChatOps AI — DevSecOps Automation Platform

![ChatOps Banner](https://github.com/user-attachments/assets/22c58201-4b21-4e16-a552-0167dd5c7891)

## 📌 Overview

ChatOps AI is a complete end-to-end DevSecOps automation platform designed for deploying and monitoring an AI-powered chatbot infrastructure.

This project combines:

* ⚡ FastAPI backend API
* 🎨 Next.js frontend interface
* 🐳 Docker & Docker Compose containerization
* 🔁 CI/CD automation with GitHub Actions
* ☁️ AWS EC2 deployment
* 📊 Monitoring with Prometheus & Grafana
* 🔐 Basic DevSecOps practices
* 🤖 AI-powered chatbot architecture

The objective of this project is to simulate a production-ready DevOps environment while integrating modern AI technologies and automation workflows.

---

# 🏗️ Architecture

```text
                    ┌────────────────────┐
                    │    GitHub Repo     │
                    └─────────┬──────────┘
                              │
                     GitHub Actions CI/CD
                              │
                              ▼
                    ┌────────────────────┐
                    │     AWS EC2        │
                    └─────────┬──────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
 ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
 │  Next.js App   │ │ FastAPI API    │ │ Monitoring     │
 │ Frontend       │ │ Backend        │ │ Grafana/Prom   │
 └────────────────┘ └────────────────┘ └────────────────┘
```

---

# ✨ Features

## 🔹 Frontend

* Modern responsive UI
* Next.js 16 + React
* Tailwind CSS styling
* AI chat interface
* Real-time API communication
* Optimized production build

## 🔹 Backend

* FastAPI REST API
* OpenAI-ready architecture
* Healthcheck endpoints
* Metrics endpoints
* Async request handling
* Containerized deployment

## 🔹 DevOps & Infrastructure

* Docker containerization
* Docker Compose orchestration
* GitHub Actions CI/CD pipeline
* AWS EC2 deployment
* Automated deployment workflow
* SSH-based production deployment

## 🔹 Monitoring

* Prometheus metrics collection
* Grafana dashboards
* Container monitoring
* Application observability

---

# 🛠️ Tech Stack

| Category        | Technologies                             |
| --------------- | ---------------------------------------- |
| Frontend        | Next.js, React, Tailwind CSS, TypeScript |
| Backend         | FastAPI, Python                          |
| DevOps          | Docker, Docker Compose, GitHub Actions   |
| Cloud           | AWS EC2                                  |
| Monitoring      | Prometheus, Grafana                      |
| CI/CD           | GitHub Actions                           |
| Version Control | Git & GitHub                             |

---

# 📂 Project Structure

```bash
.
├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── app/
│   ├── public/
│   ├── package.json
│   ├── postcss.config.js
│   └── Dockerfile
│
├── monitoring/
│   └── prometheus.yml
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
│
├── docker-compose.yml
├── README.md
└── .env
```

---

# ⚙️ Local Installation

## 1️⃣ Clone the repository

```bash
git clone https://github.com/Evilfrst/Projet-Automatisation-DevOps-de-bout-en-bout-pour-un-chatbot-IA-evolutif-ChatOps.git

cd Projet-Automatisation-DevOps-de-bout-en-bout-pour-un-chatbot-IA-evolutif-ChatOps
```

---

# 🐳 Run with Docker Compose

## Start the full stack

```bash
docker compose up --build
```

## Run in background

```bash
docker compose up -d --build
```

## Stop containers

```bash
docker compose down
```

---

# 🌐 Services URLs

| Service      | URL                                                      |
| ------------ | -------------------------------------------------------- |
| Frontend     | [http://localhost:3000](http://localhost:3000)           |
| Backend API  | [http://localhost:8000](http://localhost:8000)           |
| Swagger Docs | [http://localhost:8000/docs](http://localhost:8000/docs) |
| Prometheus   | [http://localhost:9090](http://localhost:9090)           |
| Grafana      | [http://localhost:3001](http://localhost:3001)           |

---

# 🔐 Grafana Credentials

```text
Username: admin
Password: admin
```

---

# ▶️ Run Services Individually

## Backend

```bash
cd backend

pip install -r requirements.txt

uvicorn app.main:app --reload
```

---

## Frontend

```bash
cd frontend

npm install
npm run dev
```

---

# ☁️ AWS Deployment

## EC2 Requirements

* Ubuntu Server
* Docker installed
* Docker Compose installed
* Open port 22 (SSH)
* Open port 3000 (Frontend)
* Open port 8000 (Backend)
* Open port 9090 (Prometheus)
* Open port 3001 (Grafana)

---

# 🔑 Configure GitHub Secrets

In your GitHub repository:

```text
Settings → Secrets and variables → Actions
```

Add the following secrets:

| Secret Name | Description                    |
| ----------- | ------------------------------ |
| HOST        | EC2 Elastic IP                 |
| SSH_KEY     | Private SSH key (.pem content) |

---

# 🔄 CI/CD Pipeline

The GitHub Actions pipeline automatically:

* Checks out the repository
* Copies project files to EC2
* Connects through SSH
* Rebuilds Docker containers
* Deploys updated services

Deployment file:

```text
.github/workflows/deploy.yml
```

---

# 📊 Monitoring Stack

## Prometheus

Collects application and container metrics.

Configuration:

```text
monitoring/prometheus.yml
```

## Grafana

Used for:

* Dashboard visualization
* Monitoring infrastructure
* Metrics analysis
* Observability

---

# 🔥 Common Docker Commands

## View containers

```bash
docker ps
```

## View logs

```bash
docker compose logs -f
```

## Rebuild project

```bash
docker compose build --no-cache
```

## Remove unused Docker resources

```bash
docker system prune -a -f
```

---

# 🧪 Troubleshooting

## Frontend page blank

Rebuild frontend:

```bash
docker compose build --no-cache frontend
```

---

## SSH timeout during CI/CD

Verify:

* EC2 is running
* Security Group allows port 22
* Elastic IP is correctly associated
* SSH key is valid in GitHub Secrets

---

## Docker container not starting

Check logs:

```bash
docker compose logs -f frontend
```

or:

```bash
docker compose logs -f backend
```

---

# 🔒 Security Considerations

* Use Elastic IP instead of dynamic public IP
* Protect SSH private keys
* Restrict inbound rules in production
* Use environment variables for secrets
* Avoid exposing internal services publicly

---

# 📈 Future Improvements

* Kubernetes deployment
* Terraform Infrastructure as Code
* Jenkins pipeline integration
* HTTPS with Nginx & SSL
* AI model integration
* Advanced observability stack
* Multi-environment deployment
* Automated rollback strategy

---

# 👨‍💻 Author

## Tchamen Lan

DevOps • Cloud • AI • Automation • Infrastructure

---

# 📜 License

This project is intended for educational, DevOps learning, and portfolio demonstration purposes.

---

# ⭐ Support

If you like this project:

* ⭐ Star the repository
* 🍴 Fork the project
* 🚀 Improve and contribute

---

# 🚀 Final Result

A production-style AI DevSecOps platform integrating:

✅ Frontend
✅ Backend
✅ Docker
✅ CI/CD
✅ AWS Deployment
✅ Monitoring
✅ Automation
✅ DevOps Best Practices


Grafana:
http://localhost:3001

## Grafana Credentials

admin
admin

