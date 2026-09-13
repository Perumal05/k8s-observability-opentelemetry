# OpenTelemetry Collector — Notes

## Chart

```powershell
helm search repo open-telemetry/opentelemetry-collector
```

Selected:

```text
Chart version: 0.173.1
```

Check defaults:

```powershell
helm show values open-telemetry/opentelemetry-collector --version 0.173.1
```

## Deployment Mode

```yaml
mode: deployment
```

We use one Collector instance for our local Kind cluster.

We don't need a Collector on every node, so `daemonset` is unnecessary.

## Pipeline

The Collector follows:

```text
Receiver → Processor → Exporter
```

Our pipeline:

```text
FastAPI
   ↓
OTLP
   ↓
Collector
   ↓
Batch
   ↓
Jaeger
```

## OTLP Receiver

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318
```

```text
4317 → OTLP/gRPC
4318 → OTLP/HTTP
```

The endpoints are explicitly defined because empty `grpc:` / `http:` configuration was not accepted by this Collector version.

## Batch Processor

```yaml
processors:
  batch: {}
```

Groups telemetry before sending it to the exporter.

## Jaeger Exporter

```yaml
exporters:
  otlp_grpc:
    endpoint: jaeger:4317
    tls:
      insecure: true
```

The Collector sends traces to the Jaeger Kubernetes Service using OTLP/gRPC.

## Health Check

```yaml
extensions:
  health_check:
    endpoint: ${env:MY_POD_IP}:13133
```

Provides a health endpoint for the Collector.

## Service

```yaml
service:
  type: ClusterIP
```

The Collector only needs to be accessible inside the Kubernetes cluster.

## Our Configuration

```yaml
image:
  repository: otel/opentelemetry-collector-contrib

mode: deployment

config:
  receivers:
    otlp:
      protocols:
        grpc:
          endpoint: 0.0.0.0:4317
        http:
          endpoint: 0.0.0.0:4318

  processors:
    batch: {}

  exporters:
    otlp_grpc:
      endpoint: jaeger:4317
      tls:
        insecure: true

  extensions:
    health_check:
      endpoint: ${env:MY_POD_IP}:13133

  service:
    extensions:
      - health_check

    pipelines:
      traces:
        receivers:
          - otlp
        processors:
          - batch
        exporters:
          - otlp_grpc

service:
  type: ClusterIP
```

### Main purpose

```text
Receive → Process → Export
```

The Collector is the middle layer between our application and Jaeger.
