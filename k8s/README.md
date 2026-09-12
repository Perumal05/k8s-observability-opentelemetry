# Kubernetes Deployment

This folder contains the Kubernetes manifests required to deploy the OpsDesk application on a local Kind cluster.

## Directory Structure

```text
k8s/
├── clusters.yaml                  # Kind cluster configuration
├── namespace.yaml                 # OpsDesk namespace
├── configmap.yaml                 # Application configuration
├── postgres-init-configmap.yaml   # PostgreSQL initialization scripts
├── secret.yaml                    # Database credentials (not committed)
├── postgres.yaml                  # PostgreSQL deployment and service
├── backend.yaml                   # Backend deployment and service
├── frontend.yaml                  # Frontend deployment and NodePort service
└── README.md
```

## 1. Create Kind Cluster

Create the Kind Kubernetes cluster using the provided configuration:

```bash
kind create cluster --name opentelemetry --config clusters.yaml
```

Verify the cluster:

```bash
kubectl get nodes
```

<img src="../images/kind_cluster.png" alt="Kind Kubernetes cluster" width="600">

---

## 2. Configure Database Secret

Create a `secret.yaml` file inside the `k8s` directory.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: opsdesk-secret
  namespace: opsdesk
type: Opaque
stringData:
  DATABASE_PASSWORD: "<Your DB password>"
  POSTGRES_PASSWORD: "<Your DB password>"
```

> Do not commit the actual `secret.yaml` file if it contains a real password.

---

## 3. Deploy PostgreSQL

Apply the namespace, configuration, secret, and PostgreSQL manifests:

```bash
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f postgres-init-configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f postgres.yaml
```

Check the PostgreSQL resources:

```bash
kubectl get pods -n opsdesk
```

<img src="../images/postgres_k8s_output.png" alt="PostgreSQL deployment on Kubernetes" width="600">

---

## 4. Load Application Images into Kind

Build the frontend and backend Docker images from the `opsdesk` project first.

Use the following image names:

```text
opsdesk/frontend:0.1
opsdesk/backend:0.1
```

Load the images into the Kind cluster:

```bash
kind load docker-image opsdesk/frontend:0.1 --name opentelemetry
kind load docker-image opsdesk/backend:0.1 --name opentelemetry
```

<img src="../images/kind_images.png" alt="Docker images loaded into Kind cluster" width="600">

---

## 5. Deploy Backend and Frontend

Deploy the backend:

```bash
kubectl apply -f backend.yaml
```

Deploy the frontend:

```bash
kubectl apply -f frontend.yaml
```

Check the deployments and pods:

```bash
kubectl get pods -n opsdesk
kubectl get services -n opsdesk
```

<img src="../images/frontend_backend.png" alt="Frontend and backend Kubernetes deployment" width="600">

---

## 6. Access OpsDesk

The frontend is exposed using a Kubernetes `NodePort`.

Open the application in your browser:

```text
http://localhost:30080/
```

<img src="../images/nodeport_output.png" alt="OpsDesk application accessed through NodePort" width="600">

---

## 7. Useful Commands

Check all resources:

```bash
kubectl get all -n opsdesk
```

Check pods:

```bash
kubectl get pods -n opsdesk
```

Check services:

```bash
kubectl get svc -n opsdesk
```

View backend logs:

```bash
kubectl logs -l app=opsdesk-backend -n opsdesk
```

View frontend logs:

```bash
kubectl logs -l app=opsdesk-frontend -n opsdesk
```

Delete the application resources:

```bash
kubectl delete -f frontend.yaml
kubectl delete -f backend.yaml
kubectl delete -f postgres.yaml
```

Delete the Kind cluster:

```bash
kind delete cluster --name opentelemetry
```
