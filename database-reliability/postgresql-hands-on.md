# PostgreSQL SRE Hands-On Notes

## Container lab

The local lab used PostgreSQL 17 and a test database. Credentials are intentionally omitted from this repository.

## Activity

```sql
SELECT pid, state, wait_event_type, wait_event, query
FROM pg_stat_activity;
```

Interpretation matters more than memorizing output:

- `active` means the backend is executing or waiting within a query.
- inspect `wait_event_type` and `wait_event` before concluding it is CPU-bound.

## Long query simulation

```sql
SELECT pg_sleep(300);
```

This demonstrated a session that is active but waiting on a timeout/sleep event.

## Lock/blocking lab

A transaction modified an account row and stayed open.

Another transaction attempted to modify the same row and became blocked.

Find blockers:

```sql
SELECT pg_blocking_pids(<blocked_pid>);
```

Key lesson:

`idle in transaction` is dangerous because the client may appear idle while the open transaction still holds locks.

## Operational decision

Preferred response:

```text
Identify blocker
→ inspect business context
→ allow/ask transaction to commit or rollback
→ terminate only when necessary
```

`pg_cancel_backend()` cancels an active query but may not remove locks held by an idle open transaction.

`pg_terminate_backend()` ends the session and should be treated as an impact-bearing mitigation.

## Slow query incident

Injected:

```sql
SELECT version(), pg_sleep(3);
```

Observed in `pg_stat_activity`:

```text
wait_event_type = Timeout
wait_event      = PgSleep
```

Correlated with application latency metrics and trace spans.

## Interview summary

> I do not start by killing sessions. I first identify whether the session is blocked or blocking, inspect wait events and the transaction state, assess impact, and choose the least disruptive mitigation. After mitigation I verify both database behavior and application recovery.
