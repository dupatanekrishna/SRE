# SRE Core Concepts — Fast Revision

## Golden Signals

```text
Latency
Traffic
Errors
Saturation
```

## SLI

What is measured.

Examples:

- request success rate
- availability
- p95 latency

## SLO

Internal reliability target.

Example:

```text
99.9% successful requests
```

## SLA

Contractual/business commitment.

## Error Budget

```text
100% - SLO
```

## MTTD

Mean Time To Detect.

## MTTR

Mean Time To Restore/Recover.

## Incident response

```text
Detect
→ Alert
→ Acknowledge
→ Assess impact
→ Investigate
→ Mitigate
→ Verify
→ Communicate
→ RCA
```

## Severity

Company definitions vary. Generic example:

```text
SEV1 = major outage / critical impact
SEV2 = significant degradation
SEV3 = limited impact
```

## Good alerting

Prefer user-impacting symptoms over noisy infrastructure thresholds.

Better:

- error rate
- latency
- availability
- connection exhaustion
- replication lag
- storage exhaustion

Less useful by itself:

```text
CPU > 70%
```

High CPU may simply indicate healthy utilization.

## RCA

```text
Impact
Timeline
Detection
Root cause
Contributing factors
Mitigation
Recovery validation
Preventive actions
Owners
```
