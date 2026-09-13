# Jaeger — Notes

## Chart

```powershell
helm search repo jaegertracing
```

Selected:

```text
Chart: jaegertracing/jaeger
Chart version: 4.13.1
App version: 2.20.0
```

Check defaults:

```powershell
helm show values jaegertracing/jaeger --version 4.13.1
```

## Jaeger Instance

```yaml
jaeger:
  enabled: true
  replicas: 1
```

We use one Jaeger instance because this is a local Kind cluster.

## Ingress

```yaml
ingress:
  enabled: false
```

We access the UI using port-forwarding instead:

```powershell
kubectl port-forward svc/jaeger 16686:16686 -n observability
```

Then:

```text
http://localhost:16686
```

## OpenTelemetry Connection

Jaeger exposes:

```text
4317 → OTLP/gRPC
4318 → OTLP/HTTP
```

Our Collector sends traces to:

```text
jaeger:4317
```

Flow:

```text
FastAPI
   ↓
OTLP/HTTP
   ↓
OTel Collector
   ↓
OTLP/gRPC
   ↓
Jaeger
   ↓
Jaeger UI
```

## Our Configuration

```yaml
jaeger:
  enabled: true
  replicas: 1

  service:
    annotations: {}

  ingress:
    enabled: false

networkPolicy:
  enabled: false
```

### Main purpose

Jaeger receives, stores, and displays our application traces.
