# k8s-observability-opentelemetry
End-to-end Kubernetes observability with OpenTelemetry, Prometheus, Grafana, Jaeger, and EFK using a Python FastAPI application on Kind.


--- 

Create a Kind kubernetes cluster

kind create cluster --name opentelemetry --config .\k8s\clusters.yaml

<img src="images/kind_cluster.png" alt="Opentelemtry cluster" width="700">

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
kubectl apply -f ./k8s/secret.yaml
kubectl apply -f ./k8s/postgres.yaml

<img src="images/postgres_k8s_output.png" alt="Opentelemtry cluster" width="700">