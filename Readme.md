# 🧰 DevOps for Cloud Assignment

This repository implements all tasks of the **DevOps for Cloud Course Assignment**  
using **Flask + Uvicorn**, **Docker**, **Kubernetes (Minikube)**, and **Prometheus**.

---

## 🧩 Task 1 — Create Flask Application and Run with Uvicorn

### 🎯 Objective
Develop a simple Flask API with `/get_info` endpoint and run it using **Uvicorn**.

### 🧠 Steps

1. Create working directory and activate virtual environment:

```bash
mkdir app-2024mt03553
cd app-2024mt03553
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run Flask app using Uvicorn:

```bash
uvicorn main:flask_app --host 0.0.0.0 --port 8000 --reload
```

4. Verify application:

```bash
curl http://127.0.0.1:8000/get_info
```

Output:

```json
{"APP_VERSION": "1.0", "APP_TITLE": "Devops for Cloud Assignment"}
```

5. **Screenshots to capture**

* Terminal showing Uvicorn running.
* Browser/cURL output for `/get_info`.

---

## 🐳 Task 2 — Dockerize the Application

### 🎯 Objective

Create a Docker image to containerize the Flask-Uvicorn app.

### 🧠 Steps

1. Ensure `Dockerfile` and `requirements.txt` are in project folder.

2. Build Docker image:

```bash
docker build -t img-2024mt03553 .
```

3. Verify image:

```bash
docker images | grep img-2024mt03553
```

4. **Screenshots**

* Successful Docker build log.
* Image listed with name `img-2024mt03553`.

---

## 🧱 Task 3 — Run Docker Container Locally

### 🎯 Objective

Run container and test locally.

### 🧠 Steps

1. Run container:

```bash
docker run -d --name cnr-2024mt03553 -p 8000:8000 img-2024mt03553
```

2. Check running containers:

```bash
docker ps
```

3. Verify endpoint:

```bash
curl http://127.0.0.1:8000/get_info
```

4. Stop container (optional):

```bash
docker stop cnr-2024mt03553
docker rm cnr-2024mt03553
```

5. **Screenshots**

* `docker ps` output.
* `/get_info` result.

---

## ☸️ Task 4 — Deploy on Kubernetes (Minikube)

### 🎯 Objective

Deploy the Dockerized application on a local Kubernetes cluster.

### 🧠 Steps

1. Start Minikube:

```bash
minikube start --driver=docker
```

2. Load image into Minikube:

```bash
minikube image load img-2024mt03553:latest
```

3. Apply Kubernetes manifests:

```bash
kubectl apply -f config-2024mt03553.yaml
kubectl apply -f dep-2024mt03553.yaml
```

4. Verify deployment:

```bash
kubectl get deployments
kubectl get pods -l app=flask-2024mt03553
```

5. **Screenshots**

* Deployment and pods showing **2 replicas Running**.

---

## 🌐 Task 5 — Configure LoadBalancer Service

### 🎯 Objective

Expose replicas via Kubernetes Service and demonstrate load balancing.

### 🧠 Steps

1. Apply service file:

```bash
kubectl apply -f svc-2024mt03553.yaml
```

2. Verify service:

```bash
kubectl get svc svc-2024mt03553
```

3. Get service URL:

```bash
minikube service svc-2024mt03553 --url
```

Example:

```
http://127.0.0.1:49917
```

4. Test API via service:

```bash
curl http://127.0.0.1:49917/get_info
```

5. Generate multiple requests:

```bash
for i in {1..10}; do curl -s http://127.0.0.1:49917/get_info > /dev/null; done
```

6. View logs of each pod:

```bash
kubectl get pods -l app=flask-2024mt03553
kubectl logs <pod-name-1>
kubectl logs <pod-name-2>
```

✅ Both pods should show requests, proving load balancing.

7. **Screenshots**

* Service URL & curl output.
* Logs from both pods handling traffic.

---

## 📈 Task 6 — Deploy Prometheus for Monitoring

### 🎯 Objective

Monitor application metrics such as request count using Prometheus.

### 🧠 Steps

1. Deploy Prometheus:

```bash
kubectl apply -f prometheus/prometheus-deploy.yaml
```

2. Verify Prometheus pods and services:

```bash
kubectl get pods -l app=prometheus-2024mt03553
kubectl get svc prometheus-service-2024mt03553
```

3. Access Prometheus dashboard:

```bash
minikube service prometheus-service-2024mt03553 --url
```

4. Generate sample traffic:

```bash
for i in {1..30}; do curl -s http://127.0.0.1:49917/get_info > /dev/null; done
```

5. In Prometheus UI → **Graph** tab → Query:

```
requests_total
```

You’ll see per-pod metrics.

6. **Screenshots**

* Prometheus UI (Targets page and `requests_total` graph).

---

## 🗜️ Task 7 — Prepare Submission Zip

### 🎯 Objective

Bundle all required code and screenshots for submission.

### 🧠 Steps

1. Ensure following files exist:

```
main.py
requirements.txt
Dockerfile
config-2024mt03553.yaml
dep-2024mt03553.yaml
svc-2024mt03553.yaml
prometheus/prometheus.yml
prometheus/prometheus-deploy.yaml
```

2. Create zip file:

```bash
zip -r 2024mt03553_dc.zip *
```

3. Include PDF report with:

* Task-wise screenshots
* Observations and challenges

---

## ✅ Quick Command Summary

| Task | Goal                | Key Commands                                         |
| ---- | ------------------- | ---------------------------------------------------- |
| 1    | Run Flask + Uvicorn | `uvicorn main:flask_app --port 8000`                 |
| 2    | Dockerize App       | `docker build -t img-2024mt03553 .`                  |
| 3    | Run Container       | `docker run -d -p 8000:8000 img-2024mt03553`         |
| 4    | Deploy to K8s       | `kubectl apply -f dep-2024mt03553.yaml`              |
| 5    | Load Balancer       | `kubectl apply -f svc-2024mt03553.yaml`              |
| 6    | Prometheus          | `kubectl apply -f prometheus/prometheus-deploy.yaml` |
| 7    | Submit              | `zip -r 2024mt03553_dc.zip *`                        |

---

```

If you want, I can commit this `README.md` to your repository for you — say “commit it” and I’ll provide the exact git commands to run (or run them for you if you want me to generate the commit commands).
```
