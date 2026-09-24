# Database Reliability

## RTO and RPO

- **RTO**: acceptable time to restore service after failure.
- **RPO**: acceptable amount of data loss measured as a point in time.

## HA vs DR

### Multi-AZ
Primary purpose: high availability and automated failover.

### Read replica
Primary purpose: read scaling; in some designs it can also support disaster recovery after promotion.

### Backup / snapshot
Primary purpose: recovery point and restore.

## Snapshot-based DR flow

```text
Production DB
   ↓
Backup / Snapshot
   ↓
Cross-account / Cross-region copy
   ↓
Restore
   ↓
Validate schema, tables, row counts, connectivity
   ↓
Application cutover
   ↓
Monitor
```

A backup is not proven disaster recovery until the restore process has been tested.

## PostgreSQL lock/blocking troubleshooting

Useful flow:

```text
Find blocked session
   ↓
Find blocker
   ↓
Assess transaction and business impact
   ↓
Commit/rollback if possible
   ↓
Terminate only when justified
```

`idle in transaction` sessions can continue to hold locks.

## Reliability signals for databases

- connection failures
- connection pool exhaustion
- CPU pressure
- memory pressure
- storage/IOPS saturation
- replication lag
- slow queries
- locks/deadlocks
- disk/storage exhaustion
- failed failovers
- backup/restore failures
