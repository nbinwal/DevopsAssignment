## 📂 Required Project Files

Create a directory named `app-2024mt03553` and place the following six files inside.

---

### 1. `main.py` (Task 1 & 6)

This file creates the Flask application, the `/get_info` endpoint, and the Prometheus metric collector, which tracks request count. The Prometheus server is started on port **8000**.

```python
import os
from flask import Flask, jsonify, Response
from prometheus_client import generate_latest, Counter # Use generate_latest

# ----------------- Prometheus Metrics Setup (Task 6) -----------------
# Define a counter for total requests to the /get_info endpoint
REQUEST_COUNT = Counter(
    'http_requests_total', 
    'Total requests received by the application', 
    ['method', 'endpoint', 'status']
)

# ----------------- Flask Application Setup (Task 1) -----------------
app = Flask(__name__)

# Read environment variables
APP_VERSION = os.environ.get('APP_VERSION', '1.0')
APP_TITLE = os.environ.get('APP_TITLE', 'Devops for Cloud Assignment')

@app.route('/get_info')
def get_info():
    """Returns application version and title in a JSON object."""
    
    # Increment the counter for a successful request
    REQUEST_COUNT.labels('GET', '/get_info', 200).inc()

    response_data = {
        "APP_TITLE": APP_TITLE, 
        "APP_VERSION": APP_VERSION
    }
    return jsonify(response_data)

@app.route('/metrics') # Task 6: Dedicated route for Prometheus to scrape
def metrics():
    """Returns the Prometheus metrics data."""
    # This generates the latest metrics and serves them over the Flask app (Gunicorn worker)
    return Response(generate_latest(), mimetype='text/plain')

if __name__ == '__main__':
    # This block is for local development only
    app.run(host='0.0.0.0', port=8000, debug=True)
```

---

### 2. `requirements.txt` (Task 1)

```text
Flask
gunicorn
prometheus-client
uvicorn
```

---

### 3. `Dockerfile` (Task 2)

Builds the image named `img-2024mt03553` using a base image (`python:3.11-slim`) and exposes port 8000.

```dockerfile
# Use a Python slim base image
FROM python:3.11-slim as base

# Set the working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY main.py .

# Expose the port the app runs on
EXPOSE 8000

# Run the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "main:app"]
```

---

### 4. `config-2024mt03553.yaml` (Task 4)

Creates the ConfigMap named `config-2024mt03553`.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: config-2024mt03553
data:
  APP_VERSION: "1.0"
  APP_TITLE: "Devops for Cloud Assignment"
```

---

### 5. `dep-2024mt03553.yaml` (Task 4)

Creates a Deployment named `dep-2024mt03553` running **2 replicas** and injecting environment variables from the ConfigMap.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dep-2024mt03553
  labels:
    app: flask-app-2024mt03553
spec:
  replicas: 2 
  selector:
    matchLabels:
      app: flask-app-2024mt03553
  template:
    metadata:
      labels:
        app: flask-app-2024mt03553
    spec:
      containers:
      - name: flask-app-container
        image: img-2024mt03553
        imagePullPolicy: Never # Required for locally built images in Minikube
        ports:
        - containerPort: 8000
        env:
        # Read variables from the ConfigMap
        - name: APP_VERSION
          valueFrom:
            configMapKeyRef:
              name: config-2024mt03553
              key: APP_VERSION
        - name: APP_TITLE
          valueFrom:
            configMapKeyRef:
              name: config-2024mt03553
              key: APP_TITLE
```

---

### 6. `svc-2024mt03553.yaml` (Task 5 & 6)

Creates a **LoadBalancer Service** named `svc-2024mt03553` with the necessary Prometheus annotations.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: svc-2024mt03553
  labels:
    app: flask-app-2024mt03553
  annotations:
    # Prometheus annotations for automatic metric scraping (Task 6)
    prometheus.io/scrape: "true"
    prometheus.io/port: "8000"     # Container port exposed by the app
    prometheus.io/path: "/metrics" # Metrics path
spec:
  selector:
    app: flask-app-2024mt03553
  ports:
    - protocol: TCP
      port: 80 
      targetPort: 8000 
  type: LoadBalancer # Configures Load Balancer functionality
```

---

## 💻 Execution and Verification Steps

### Task 1: Create the Backend Application

1. **Install dependencies and activate venv:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run Locally (using Gunicorn for stability):**

   ```bash
   export APP_VERSION="1.0"
   export APP_TITLE="Devops for Cloud Assignment"
   gunicorn --bind 0.0.0.0:8000 main:app
   ```

3. **Verify Endpoint:** Open `http://localhost:8000/get_info` and check the JSON response.

4. **Stop Server** (`Ctrl+C`) and **Deactivate:**

   ```bash
   deactivate
   ```

---

### Task 2 & 3: Dockerize and Run Container

1. **Set Minikube Context** (Required to build the image inside Minikube's Docker daemon):

   ```bash
   minikube start
   eval $(minikube docker-env)
   ```

2. **Build Docker Image:**

   ```bash
   docker build -t img-2024mt03553 .
   ```

3. **Verify Image Creation:**

   ```bash
   docker images img-2024mt03553
   ```

4. **Run Container (Task 3 Verification):**

   ```bash
   docker run -d --name cnr-2024mt03553 -p 8000:8000 img-2024mt03553
   ```

5. **Verify Application Access:** Access `minikube ip`
`http://<MINIKUBE_IP>:8000/get_info`.

6. **Stop and Remove Container:**

   ```bash
   docker stop cnr-2024mt03553 && docker rm cnr-2024mt03553
   ```

---

### Task 4 & 5: Kubernetes Deployment and Load Balancing

1. **Apply Manifests:**

   ```bash
   kubectl apply -f config-2024mt03553.yaml
   kubectl apply -f dep-2024mt03553.yaml
   kubectl apply -f svc-2024mt03553.yaml
   ```

2. **Verify Pods and Service Status:**

   ```bash
   kubectl get deployments,pods,svc
   ```

3. **Get LoadBalancer URL (Minikube access):**

   ```bash
   minikube service svc-2024mt03553 --url
   ```

4. **Verify Load Balancing (Proof of Task 5):**

   * **Terminal 1 & 2:** Start watching logs for both Pods (get actual Pod names from `kubectl get pods`):

     ```bash
     kubectl logs -f <POD_1_NAME>
     kubectl logs -f <POD_2_NAME>
     ```
   * **Terminal 3:** Run curl requests (use the URL from Step 3, e.g., `http://127.0.0.1:50056`):

     ```bash
     SERVICE_URL=http://127.0.0.1:XXXXX 
     for i in {1..20}; do curl $SERVICE_URL/get_info; done
     ```
   * **Capture a screenshot** showing logs appearing alternately in the two log windows for proof of balancing.

---

### Task 6: Configure Prometheus for Metrics Collection

1. **Install Prometheus Stack** (Requires Helm, assuming it is installed):

   ```bash

   # 1. Apply ConfigMap
   kubectl apply -f prometheus-config.yaml

   # 2. Apply Deployment and Service
   kubectl apply -f prometheus-deployment.yaml
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm repo update
   helm install prometheus prometheus-community/kube-prometheus-stack
   ```

2. **Port-Forward Prometheus** (Run in a dedicated terminal and leave open):

   ```bash
   kubectl port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090
   ```

3. **Query Metrics (Submit Screenshots):** Open `http://localhost:9090` and run the following queries, capturing a screenshot of the graph result for each.

| Metric Required   | PromQL Query                                                                          | Notes                                             |
| :---------------- | :------------------------------------------------------------------------------------ | :------------------------------------------------ |
| **Request Count** | `http_requests_total`                                                                 | Requires running the curl loop from Task 5 first. |
| **CPU Usage**     | `sum(rate(container_cpu_usage_seconds_total{pod=~"dep-2024mt03553.*"}[5m])) by (pod)` | Tracks resource usage per replica.                |
| **Memory Usage**  | `container_memory_working_set_bytes{pod=~"dep-2024mt03553.*"}`                        | Tracks resource usage per replica.                |

---

### 📦 Final Submission

Package the following files into a zip file named **`2024MT03553_dc.zip`**:

1. `main.py`
2. `requirements.txt`
3. `Dockerfile`
4. `config-2024mt03553.yaml`
5. `dep-2024mt03553.yaml`
6. `svc-2024mt03553.yaml`
7. A **PDF document** with screen captures of output showcasing all tasks.
   *Note*: In the document, state that the Prometheus configuration files were handled by the `kube-prometheus-stack` Helm chart.
