# k8s-observability-opentelemetry
End-to-end Kubernetes observability with OpenTelemetry, Prometheus, Grafana, Jaeger, and EFK using a Python FastAPI application on Kind.


--- 

Create a Kind kubernetes cluster

kind create cluster --name opentelemetry --config .\k8s\clusters.yaml

<img src="../images/kind_cluster.png" alt="Opentelemtry cluster" width="700">

create a secret.yaml with the below DB password with the filename k8s/secret.yaml

apiVersion: v1
kind: Secret
metadata:
  name: opsdesk-secret
  namespace: opsdesk
type: Opaque
stringData:
  DATABASE_PASSWORD: "<Your DB password>"
  POSTGRES_PASSWORD: "<Your DB password>"


kubectl apply -f ./k8s/namespace.yaml
kubectl apply -f ./k8s/configmap.yaml
kubectl apply -f ./k8s/postgres-init-configmap.yaml
kubectl apply -f ./k8s/secret.yaml
kubectl apply -f ./k8s/postgres.yaml

<img src="../images/postgres_k8s_output.png" alt="Opentelemtry cluster" width="700">

Load the docker images into Kind cluster. Just before this build the images for frontend and backend using the dockerfile under opsdesk source reposiotry, with the below naming conventions:

kind load docker-image opsdesk/frontend:0.1 --name opentelemetry
kind load docker-image opsdesk/backend:0.1 --name opentelemetry

<img src="../images/kind_images.png" alt="Docker images loaded into Kind cluster" width="700">


kubectl apply -f ./k8s/backend.yaml
kubectl apply -f ./k8s/frontend.yaml

<img src="../images/frontend_backend.png" alt="Deployment output of frontend and backend" width="700">

Since we exposed our frontend as nodeport, we can access the application using localhost

http://localhost:30080/

<img src="../images/nodeport_output.png" alt="Deployment output of frontend and backend" width="700">
