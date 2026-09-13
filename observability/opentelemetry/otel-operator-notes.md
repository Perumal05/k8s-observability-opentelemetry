# OpenTelemetry Operator — Notes

## Chart

```powershell
helm search repo open-telemetry/opentelemetry-operator
```

Selected:

```text
Chart version: 0.122.0
```

Check defaults:

```powershell
helm show values open-telemetry/opentelemetry-operator --version 0.122.0
```

## Admission Webhook

```yaml
admissionWebhooks:
  create: true
```

Enables the Operator webhook used for features such as **auto-instrumentation injection**.

## Webhook Certificates

We are not using cert-manager:

```yaml
certManager:
  enabled: false
```

Instead, Helm generates the certificates:

```yaml
autoGenerateCert:
  enabled: true
  recreate: true
  certPeriodDays: 365
```

This avoids installing an additional certificate-management component.

## CRDs

```yaml
crds:
  create: true
```

Creates the OpenTelemetry Kubernetes resources required by the Operator, such as:

```text
Instrumentation
OpenTelemetryCollector
```

## Our Configuration

```yaml
admissionWebhooks:
  create: true
  servicePort: 443
  failurePolicy: Fail

  certManager:
    enabled: false

  autoGenerateCert:
    enabled: true
    recreate: true
    certPeriodDays: 365

crds:
  create: true
```

### Main purpose

```text
OpenTelemetry Operator
        ↓
Manages OpenTelemetry resources
        ↓
Injects auto-instrumentation
```
