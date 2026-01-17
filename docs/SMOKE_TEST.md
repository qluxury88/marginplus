# 🧪 MarginPlus — Smoke Test (Read-only Verification)

This document defines the **read-only smoke test procedure**
for MarginPlus MVP v2.0.

The purpose is to verify **system readiness and health**
without execution, mutation, or prediction.

---

## 📐 Canon Metadata

- Project: MarginPlus
- Version / Phase: MVP v2.0 (Phase A)
- ROLE: VERIFICATION
- MODE: Evidence-only / Read-only
- STATUS: LOCKED
- Owner: ODS / MarginPlus Core

---

## 🎯 Purpose

This document exists to:

- Verify that the system is **alive, stable, and safe**
- Detect obvious failure states early
- Provide **human-readable confidence** before any next action

🛡️ This test is designed to be safe to run at any time.

---

## 🧭 Scope & Boundaries

### Covered
- Backend health availability
- Status artifact freshness
- Scheduler / cron last-known state
- Evidence log existence

### Not Covered
- ❌ Trading
- ❌ Prediction
- ❌ Signal evaluation
- ❌ State mutation
- ❌ Phase B features

---

## 🩺 Step 1 — Backend Health Probe

Run on the **runtime server**:

```bash
for i in {1..10}; do
  curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8090/health
done
