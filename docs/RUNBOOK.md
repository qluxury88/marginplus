# MarginPlus Runbook (Read-only)

This runbook describes **operational checks only** for MarginPlus MVP
v2.0. No execution, no trading, and no state mutation are permitted.

------------------------------------------------------------------------

## 📐 System Role

-   Phase: MVP v2.0 (SPEC LOCKED)
-   Mode: L0--L2, read-only
-   Purpose:
    -   Decision readiness
    -   State awareness
    -   Auditability

This system **does NOT**: - Execute trades - Generate predictions -
Mutate production state

------------------------------------------------------------------------

## 🩺 Health Check

### Backend Health (Local)

Run on the runtime server:

    curl http://127.0.0.1:8090/health

Expected result: - HTTP `200` - No timeout - No `502`

> Note: Proxy endpoint `/health` may return `308` due to HTTPS redirect.
> This is expected and **not a failure**.

------------------------------------------------------------------------

## 📊 Status Artifacts (Read-only)

The following files represent the **source of truth** for system status:

    /opt/marginplus/data/latest/mp_status_latest.json
    /opt/marginplus/data/latest/mp_brief_latest.md

Properties: - Read-only - Safely overwritten (latest only) - Consumed by
ODS

------------------------------------------------------------------------

## 🧪 Smoke Test (Read-only)

Use this procedure to verify readiness without execution.

    # Health probe (10 rounds)
    for i in {1..10}; do
      curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8090/health
    done

Expected: - `200` for all rounds - No `502`

    # Parse status artifact
    python3 - << 'EOF'
    import json
    d = json.load(open('/opt/marginplus/data/latest/mp_status_latest.json'))
    print("freshness_sec =", d.get("freshness_sec"))
    print("generated_at_utc =", d.get("generated_at_utc"))
    EOF

    # Check last cron status
    tail -n 1 /opt/marginplus/data/predict_evaluate_cron.log

Expected: - Status line contains `OK`

------------------------------------------------------------------------

## 📁 Logs

Operational logs are stored on the runtime server:

    /var/log/marginplus/

Smoke test evidence:

    /var/log/marginplus/smoke_test_YYYYMMDD_HHMMSS.log

------------------------------------------------------------------------

## 🔁 Rollback

-   No rollback procedure required
-   System is read-only
-   Restarting the service is safe if needed

------------------------------------------------------------------------

## ⚠️ Forbidden Actions

The following actions are strictly forbidden in MVP v2.0:

-   Auto-trade
-   Prediction logic
-   Phase B features
-   Direct production mutation

------------------------------------------------------------------------

## 🔒 Operational Notes

-   SSH access is restricted via allowlist (bastion pattern)
-   Key-based authentication only
-   Runtime server contains:
    -   no Git repository
    -   no secrets
    -   no public write access
