# OpenTelemetry

OpenTelemetry setup for the Kubernetes observability project running on a local Kind cluster.

## Architecture

![OpenTelemetry Architecture](../../images/otel_architecture.png)

```text
FastAPI
   ↓
OTLP/HTTP
   ↓
OpenTelemetry Collector
   ↓
OTLP/gRPC
   ↓
Jaeger
   ↓
Jaeger UI
```

## 1. Create the Observability Namespace

```powershell
kubectl apply -f observability/namespace.yaml
```

## 2. Add the OpenTelemetry Helm Repository

```powershell
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts
helm repo update
helm repo list
```

Check the available charts:

```powershell
helm search repo open-telemetry
```

![OpenTelemetry Helm Repository](../../images/opentelemetry_repo.png)

## 3. Install the OpenTelemetry Operator

Check the chart values:

```powershell
helm show values open-telemetry/opentelemetry-operator --version 0.122.0
```

Install the Operator:

```powershell
helm upgrade --install opentelemetry-operator `
  open-telemetry/opentelemetry-operator `
  --namespace observability `
  --version 0.122.0 `
  --values observability/opentelemetry/values.yaml
```

![OpenTelemetry Operator Installation](../../images/operator_install_output.png)

The Operator manages OpenTelemetry resources and handles auto-instrumentation.

For the Operator configuration, see [otel-operator-notes.md](./otel-operator-notes.md).

## 4. Install the OpenTelemetry Collector

Check the chart values:

```powershell
helm show values open-telemetry/opentelemetry-collector --version 0.173.1
```

Install the Collector:

```powershell
helm upgrade --install opentelemetry-collector `
  open-telemetry/opentelemetry-collector `
  --namespace observability `
  --version 0.173.1 `
  --values observability/opentelemetry/collector-values.yaml
```

![OpenTelemetry Collector Installation](../../images/collector_install_output.png)

Verify:

```powershell
kubectl get pods -n observability
```

The Collector receives traces from the application and exports them to Jaeger.

For the Collector configuration, see [otel-collector-notes.md](./otel-collector-notes.md).

## 5. Install Jaeger

Add the Jaeger Helm repository:

```powershell
helm repo add jaegertracing https://jaegertracing.github.io/helm-charts
helm repo update
helm search repo jaegertracing
```

![Jaeger Helm Repository](../../images/jaeger_repo.png)

For this project, we use the `jaegertracing/jaeger` chart.

Install Jaeger:

```powershell
helm upgrade --install jaeger `
  jaegertracing/jaeger `
  --namespace observability `
  --version 4.13.1 `
  --values observability/opentelemetry/jaeger-values.yaml
```

Verify:

```powershell
kubectl get pods -n observability
kubectl get svc -n observability
```

![Jaeger Verification](../../images/jaeger_verify.png)

For the Jaeger configuration, see [jaegar-notes.md](./jaegar-notes.md).

## 6. Verify Jaeger UI

Port-forward the Jaeger service:

```powershell
kubectl port-forward svc/jaeger 16686:16686 -n observability
```

Open:

```text
http://localhost:16686
```

![Jaeger UI](../../images/jaeger_ui.png)

## 7. Connect the Collector to Jaeger

The Collector and Jaeger are running in the `observability` namespace.

The Collector exports traces to:

```text
jaeger:4317
```

The Collector configuration uses OTLP/gRPC for the connection to Jaeger.

After updating `collector-values.yaml`, upgrade the Collector:

```powershell
helm upgrade --install opentelemetry-collector `
  open-telemetry/opentelemetry-collector `
  --namespace observability `
  --version 0.173.1 `
  --values observability/opentelemetry/collector-values.yaml
```

Verify:

```powershell
kubectl get pods -n observability
```

## 8. Auto-Instrument the FastAPI Backend

Create the OpenTelemetry `Instrumentation` resource:

```text
observability/opentelemetry/instrumentation.yaml
```

The instrumentation points to the Collector using:

```text
http://opentelemetry-collector.observability.svc.cluster.local:4318
```

Apply it:

```powershell
kubectl apply -f ./observability/opentelemetry/instrumentation.yaml
```

Verify:

```powershell
kubectl get instrumentation -n opsdesk
```

Add the Python instrumentation annotation to the backend Deployment:

```yaml
instrumentation.opentelemetry.io/inject-python: "opsdesk/opsdesk-python-instrumentation"
```

Apply the backend Deployment:

```powershell
kubectl apply -f k8s/backend.yaml
```

Verify the injected init container:

```powershell
kubectl describe pod -n opsdesk -l app.kubernetes.io/name=opsdesk-backend
```

![Instrumentation Annotation](../../images/instrumentation_annotation.png)

![OpenTelemetry Init Container](../../images/init_container.png)

## 9. Verify Traces in Jaeger

Open the Jaeger UI and verify that the `opsdesk-backend` service appears.

![Jaeger UI Verification](../../images/Jaeger_ui_verification.png)

## Notes

Detailed configuration and explanations are maintained separately:

* [OpenTelemetry Operator Notes](./otel-operator-notes.md)
* [OpenTelemetry Collector Notes](./otel-collector-notes.md)
* [Jaeger Notes](./jaegar-notes.md)
