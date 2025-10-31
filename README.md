# DevOps for Cloud Assignment – Roll No. **2024MT03553**

## 🛠️ Setup and Pre-requisites

Before starting, ensure you have the following installed:

* **Python 3** and `pip`
* **Docker Desktop** (or Docker engine)
* **Minikube** (or access to another Kubernetes cluster like a BITS Virtual lab or cloud service)
* `kubectl`

Your roll number for file and image naming is **2024MT03553**.
The project directory will be named `app-2024MT03553`.

---

## 📝 Task 1: Create the Backend Application (Flask & Uvicorn)

This task creates the Flask app, the `/get_info` endpoint, and uses environment variables for `APP_VERSION` and `APP_TITLE`.

### 1. Project Directory and Files

```bash
mkdir app-2024MT03553
cd app-2024MT03553
touch main.py requirements.txt
```

### 2. `requirements.txt`

The application uses Flask, `gunicorn` (a production server), `uvicorn`, and `prometheus_client` for metrics (Task 6).

```text
flask
gunicorn
uvicorn
prometheus_client
```

### 3. `main.py`

```python
import os
import json
from flask import Flask, jsonify, request
from prometheus_client import start_http_server, Counter

# --- Prometheus Configuration (Task 6) ---
REQUEST_COUNT = Counter(
    'http_requests_total', 
    'Total number of requests to the application', 
    ['method', 'endpoint']
)

app = Flask(__name__)

# --- Application Info (Task 1) ---
APP_VERSION = os.environ.get("APP_VERSION", "1.0")
APP_TITLE = os.environ.get("APP_TITLE", "Devops for Cloud Assignment")

@app.route("/get_info")
def get_info():
    REQUEST_COUNT.labels(method=request.method, endpoint='/get_info').inc()
    info = {
        "APP_VERSION": APP_VERSION,
        "APP_TITLE": APP_TITLE
    }
    return jsonify(info)

@app.route("/metrics")
def metrics():
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```

### 4. Local Execution (Task 1 Verification)

```bash
pip install -r requirements.txt

export APP_VERSION="1.0"
export APP_TITLE="Devops for Cloud Assignment"
uvicorn main:app --host 0.0.0.0 --port 8000 
```

Then verify in your browser:
**`http://localhost:8000/get_info`**

Output:

```json
{"APP_TITLE": "Devops for Cloud Assignment", "APP_VERSION": "1.0"}
```

---

## 📦 Task 2: Dockerize the Backend Application

### 1. `Dockerfile`

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "main:app"]
```

### 2. Build the Docker Image

```bash
docker build -t img-2024mt03553 .
```

Verify:

```bash
docker images | grep img-2024mt03553
```

---

## 🏃 Task 3: Run the Docker Container

### 1. Run the Container

```bash
docker run -d -p 8000:8000 \
    --name cnr-2024mt03553 \
    -e APP_VERSION="1.0" \
    -e APP_TITLE="Devops for Cloud Assignment" \
    img-2024mt03553
```

### 2. Verification

```bash
docker ps | grep cnr-2024MT03553
```

Access in browser:
`http://localhost:8000/get_info`

Stop and remove container when done:

```bash
docker stop cnr-2024MT03553
docker rm cnr-2024MT03553
```

---

## ☁️ Task 4 & 5: Kubernetes Deployment, Networking, and Load Balancer

### 1. Push Image to a Registry

If using Minikube:

```bash
minikube start
eval $(minikube docker-env)
docker build -t img-2024MT03553 .
eval $(minikube docker-env -u)
```

### 2. ConfigMap (`config-2024MT03553.yaml`)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: config-2024MT03553
data:
  APP_VERSION: "1.0"
  APP_TITLE: "Devops for Cloud Assignment"
```

### 3. Deployment (`dep-2024MT03553.yaml`)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dep-2024MT03553
  labels:
    app: flask-app-2024MT03553
spec:
  replicas: 2
  selector:
    matchLabels:
      app: flask-app-2024MT03553
  template:
    metadata:
      labels:
        app: flask-app-2024MT03553
    spec:
      containers:
      - name: flask-app-container
        image: img-2024MT03553
        imagePullPolicy: Never
        ports:
        - containerPort: 8000
        env:
        - name: APP_VERSION
          valueFrom:
            configMapKeyRef:
              name: config-2024MT03553
              key: APP_VERSION
        - name: APP_TITLE
          valueFrom:
            configMapKeyRef:
              name: config-2024MT03553
              key: APP_TITLE
```

### 4. Service/Load Balancer (`svc-2024MT03553.yaml`)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: svc-2024MT03553
spec:
  selector:
    app: flask-app-2024MT03553
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

### 5. Deployment Commands

```bash
kubectl apply -f config-2024MT03553.yaml
kubectl apply -f dep-2024MT03553.yaml
kubectl apply -f svc-2024MT03553.yaml
```

Verify:

```bash
kubectl get deployments
kubectl get pods
kubectl get svc
```

### 6. Verification (Load Balancing)

```bash
POD_1=$(kubectl get pods -l app=flask-app-2024MT03553 -o jsonpath='{.items[0].metadata.name}')
POD_2=$(kubectl get pods -l app=flask-app-2024MT03553 -o jsonpath='{.items[1].metadata.name}')

kubectl logs -f $POD_1
kubectl logs -f $POD_2

SERVICE_URL=$(minikube service svc-2024MT03553 --url)
for i in {1..10}; do curl $SERVICE_URL/get_info; done
```

You should see requests distributed across both pods.

---

## 📈 Task 6: Configure Prometheus for Metrics Collection

### 1. Install Prometheus (using Helm)

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack
```

### 2. Configure Prometheus to Scrape Your App

Update your service file to include Prometheus annotations:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: svc-2024MT03553
  labels:
    release: prometheus
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8000"
    prometheus.io/path: "/metrics"
spec:
  selector:
    app: flask-app-2024MT03553
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

Re-apply:

```bash
kubectl apply -f svc-2024MT03553.yaml
```

### 3. Verification and Prometheus Queries

Port-forward to Prometheus:

```bash
kubectl port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090
```

Access: **[http://localhost:9090](http://localhost:9090)**

#### Queries:

* **Request Count:**

  ```
  http_requests_total
  ```
* **CPU Usage:**

  ```promql
  sum(rate(container_cpu_usage_seconds_total{pod=~"dep-2024MT03553.*"}[5m])) by (pod)
  ```
* **Memory Usage:**

  ```promql
  container_memory_working_set_bytes{pod=~"dep-2024MT03553.*"}
  ```

Take screenshots of these graphs for submission.

---

## 📦 Submission File List

Include the following in your final zip file **`2024MT03553_dc.zip`**:

1. `main.py`
2. `requirements.txt`
3. `Dockerfile`
4. `config-2024MT03553.yaml`
5. `dep-2024MT03553.yaml`
6. `svc-2024MT03553.yaml`
7. Prometheus configuration files (if applicable)
8. A **PDF document** with step-by-step documentation, screenshots, and notes on challenges faced.

---
