📐 Canon — MarginPlus MVP marginplus_mvp_pack_v2_0
Scope: /latest + /status + /health
Time: v2.0 · 2026

🧱 Invariant: Phase A must close before Phase B
🛡️ Governance: Evidence-only
🧨 Boundary: No prediction in Phase 1

Paths
- Data source (read-only): D:\marginplus-capture\mp_windows_latest.json
- MVP code: D:\marginplus_mvp
- Audit: D:\marginplus_mvp\audit\mp_api_audit.jsonl
- State: D:\marginplus_mvp\state\mp_status_state.json

Run
1) PowerShell:
   cd /d D:\marginplus_mvp
   python -m uvicorn app:app --reload
2) Or double-click run.bat (if .bat allowed)

Open
- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/status
- http://127.0.0.1:8000/latest

📐 SPEC FREEZE — MarginPlus MVP v2.0
Status: LOCKED
Date: 2026-01-02

Included:
- /latest
- /status
- /health
- Audit JSONL (append-only)
- State tracking + STATE_CHANGED (cooldown)

Excluded:
- Phase B (10m)
- Signals / Prediction
- Notifications (UI/Push)

Rule:
- No feature changes in v2.0
- Bugfix only (no behavior change)