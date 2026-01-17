# MarginPlus — MVP v2.0 (Spec Locked)

MarginPlus is an **AI-assisted, evidence-only decision readiness system**  
focused on auditability, state awareness, and disciplined execution.

This repository documents the **public-safe specification and operations**  
of MarginPlus MVP v2.0.

---

## 📐 Canon — MarginPlus MVP v2.0
- **Scope:** `/latest`, `/status`, /health
- **Time:** v2.0 · 2026
- **Status:** SPEC FREEZE (LOCKED)

### Invariants
- 🧱 Phase A must close before Phase B
- 🛡️ Governance: Evidence-only
- 🧨 Boundary: No prediction in Phase 1

---

## ✅ Included (v2.0)
- /latest
- /status
- /health
- Audit logs (JSONL, append-only)
- State tracking + STATE_CHANGED with cooldown

## ❌ Excluded (v2.0)
- Phase B (10m timeframe)
- Signals / Prediction
- Notifications (UI / Push)
- Any form of auto-trade or execution

> **Rule:**  
> No feature changes in v2.0  
> Bugfix only (no behavior change)

---

## 🧠 Architecture (Current)
- **Runtime server:** tv-webhook-phase2
- **Mode:** L0–L2, read-only
- **Execution:** Disabled (no trading)

### Health
- Backend health (local):
  - http://127.0.0.1:8090/health
- Note: Proxy /health may return 308 due to HTTPS redirect

### Status Artifacts (Server paths)
- /opt/marginplus/data/latest/mp_status_latest.json
- /opt/marginplus/data/latest/mp_brief_latest.md

---

## 🧪 Smoke Test (Read-only)
A fresh user can verify system readiness without execution:

1. Call backend health 10 times → expect 200
2. Parse mp_status_latest.json
3. Check freshness_sec is reasonable
4. Verify last cron status is OK
5. Ensure no 502 during probe window

Evidence logs are stored on the server:
- /var/log/marginplus/smoke_test_YYYYMMDD_HHMMSS.log

---

## 🔒 Security Posture (Summary)
- SSH allowlist (bastion / jump-host pattern)
- Key-based access only
- Runtime server contains:
  - no Git repository
  - no secrets
  - no public write access

---

## 📄 License
MIT
