from fastapi import FastAPI
from pathlib import Path
import json
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional, Tuple

# ======================
# 📐 CANON (Locked)
# ======================
CANON: Dict[str, Any] = {
    "tag": "📐 Canon",
    "scope": "MarginPlus · Phase 1",
    "time": "v2.0 · 2026",
    "rules": [
        "🧱 Invariant: Phase A must close before Phase B",
        "🛡️ Governance: Evidence-only",
        "🧨 Boundary: No prediction in Phase 1",
    ],
}

# ======================
# VERSION / PACK ID
# ======================
APP_VERSION = "v2.0"
PACK_ID = "marginplus_mvp_pack_v2_0_metrics"

# ======================
# CONFIG (Locked)
# ======================
LATEST_FILE = Path(r"D:\marginplus-capture\mp_windows_latest.json")

# Phase 1 cadence (1H expected; stale if >2H)
EXPECTED_SEC = 3600
STALE_SEC = 7200

# File has generated_at_local in Thailand time
LOCAL_TZ = timezone(timedelta(hours=7))

# Audit (append-only) — Canon location (MVP sandbox)
AUDIT_DIR = Path(r"D:\marginplus_mvp\audit")
AUDIT_FILE = AUDIT_DIR / "mp_api_audit.jsonl"

# State tracking (for cross-run memory + future notifications)
STATE_DIR = Path(r"D:\marginplus_mvp\state")
STATE_FILE = STATE_DIR / "mp_status_state.json"

# Cooldown for STATE_CHANGED events (seconds)
STATE_CHANGE_COOLDOWN_SEC = 600  # 10 minutes

app = FastAPI(title="MarginPlus MVP", version=APP_VERSION)

# Metrics uptime start
START_TIME_UTC = datetime.now(timezone.utc)

# ----------------------
# Helpers
# ----------------------
def _now_utc() -> datetime:
    return datetime.now(timezone.utc)

def _iso_z(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")

def _canon_header() -> Dict[str, Any]:
    return {
        "canon": CANON,
        "version": APP_VERSION,
        "pack_id": PACK_ID,
    }

def _audit(event: Dict[str, Any]) -> None:
    """
    Append-only audit log.
    IMPORTANT: must never break API responses.
    """
    try:
        AUDIT_DIR.mkdir(parents=True, exist_ok=True)
        with open(AUDIT_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        pass

def _safe_load_json(file_path: Path) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    if not file_path.exists():
        return None, f"Latest file not found: {file_path}"
    try:
        text = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return None, f"Read failed: {type(e).__name__}: {e}"
    try:
        data = json.loads(text)
    except Exception as e:
        return None, f"JSON parse failed: {type(e).__name__}: {e}"
    if not isinstance(data, dict):
        return None, "Invalid JSON shape: expected object (dict)"
    return data, None

def _parse_snapshot_time_utc(value: Any) -> Optional[datetime]:
    if not isinstance(value, str) or not value:
        return None
    try:
        iso = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(iso)
        if dt.tzinfo is None:
            return None
        return dt.astimezone(timezone.utc)
    except Exception:
        return None

def _parse_generated_at_local(value: Any) -> Optional[datetime]:
    if not isinstance(value, str) or not value:
        return None
    try:
        dt_local = datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(tzinfo=LOCAL_TZ)
        return dt_local.astimezone(timezone.utc)
    except Exception:
        return None

def _file_mtime_utc(file_path: Path) -> Optional[datetime]:
    try:
        return datetime.fromtimestamp(file_path.stat().st_mtime, tz=timezone.utc)
    except Exception:
        return None

def _choose_best_timestamp(data: Dict[str, Any]) -> Tuple[Optional[datetime], str]:
    """
    Returns (dt_utc, source_label)
    priority: snapshot_time_utc -> generated_at_local -> file_mtime
    """
    dt = _parse_snapshot_time_utc(data.get("snapshot_time_utc"))
    if dt:
        return dt, "snapshot_time_utc"

    dt2 = _parse_generated_at_local(data.get("generated_at_local"))
    if dt2:
        return dt2, "generated_at_local"

    dt3 = _file_mtime_utc(LATEST_FILE)
    if dt3:
        return dt3, "file_mtime"

    return None, "none"

def _load_last_state() -> Optional[Dict[str, Any]]:
    try:
        if not STATE_FILE.exists():
            return None
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return None

def _save_last_state(payload: Dict[str, Any]) -> None:
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass

def _can_emit_state_change(last_state_obj: Optional[Dict[str, Any]], now: datetime) -> bool:
    """
    Prevent noisy repeats. Uses last_state_obj["last_change_ts_utc"] if present.
    """
    try:
        if not last_state_obj:
            return True
        last_change = last_state_obj.get("last_change_ts_utc")
        if not last_change:
            return True
        dt = datetime.fromisoformat(str(last_change).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            return True
        elapsed = (now - dt.astimezone(timezone.utc)).total_seconds()
        return elapsed >= STATE_CHANGE_COOLDOWN_SEC
    except Exception:
        return True

# ---- Metrics helpers (read-only / fail-soft)
def _safe_count_lines(path: Path) -> int:
    try:
        if not path.exists():
            return 0
        with open(path, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)
    except Exception:
        return -1  # unreadable

def _safe_read_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

# ----------------------
# Endpoints
# ----------------------
@app.get("/favicon.ico")
def favicon():
    return {}

@app.get("/health")
def health():
    ok_latest = LATEST_FILE.exists()

    ok_audit_dir = True
    ok_state_dir = True
    try:
        AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    except Exception:
        ok_audit_dir = False
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
    except Exception:
        ok_state_dir = False

    status = "OK" if (ok_latest and ok_audit_dir and ok_state_dir) else "ERROR"

    metrics = {
        "uptime_sec": int((_now_utc() - START_TIME_UTC).total_seconds()),
        "audit_lines": _safe_count_lines(AUDIT_FILE),
        "last_state": (_safe_read_json(STATE_FILE) or {}).get("state"),
    }

    return {
        **_canon_header(),
        "endpoint": "/health",
        "status": status,
        "checks": {
            "latest_file_exists": ok_latest,
            "audit_dir_writable": ok_audit_dir,
            "state_dir_writable": ok_state_dir
        },
        "metrics": metrics
    }

@app.get("/latest")
def latest():
    data, err = _safe_load_json(LATEST_FILE)
    if err:
        _audit({
            "ts_utc": _iso_z(_now_utc()),
            "endpoint": "/latest",
            "state": "ERROR",
            "file": str(LATEST_FILE),
            "error": err,
            "version": APP_VERSION,
            "pack_id": PACK_ID,
        })
        return {
            **_canon_header(),
            "endpoint": "/latest",
            "status": "ERROR",
            "file": str(LATEST_FILE),
            "error": err,
        }

    _audit({
        "ts_utc": _iso_z(_now_utc()),
        "endpoint": "/latest",
        "state": "OK",
        "file": str(LATEST_FILE),
        "version": APP_VERSION,
        "pack_id": PACK_ID,
    })

    return {
        **_canon_header(),
        "endpoint": "/latest",
        "status": "OK",
        "file": str(LATEST_FILE),
        "data": data,
        "canon_footer": "🛡️ Canon · Evidence-only · Audit-ready",
    }

@app.get("/status")
def status():
    now = _now_utc()

    data, err = _safe_load_json(LATEST_FILE)
    if err:
        _audit({
            "ts_utc": _iso_z(now),
            "endpoint": "/status",
            "state": "ERROR",
            "file": str(LATEST_FILE),
            "error": err,
            "version": APP_VERSION,
            "pack_id": PACK_ID,
        })
        return {
            **_canon_header(),
            "endpoint": "/status",
            "state": "ERROR",
            "file": str(LATEST_FILE),
            "evidence": {
                "timestamp_source": None,
                "timestamp_utc": None,
                "age_sec": None,
                "expected_interval_sec": EXPECTED_SEC,
                "staleness_limit_sec": STALE_SEC,
            },
            "errors": [err],
            "notes": "Evidence-only. No signals.",
        }

    ts_utc, ts_source = _choose_best_timestamp(data)
    if ts_utc is None:
        msg = "No usable timestamp: expected snapshot_time_utc or generated_at_local or file mtime."
        _audit({
            "ts_utc": _iso_z(now),
            "endpoint": "/status",
            "state": "ERROR",
            "file": str(LATEST_FILE),
            "error": msg,
            "version": APP_VERSION,
            "pack_id": PACK_ID,
        })
        return {
            **_canon_header(),
            "endpoint": "/status",
            "state": "ERROR",
            "file": str(LATEST_FILE),
            "evidence": {
                "timestamp_source": ts_source,
                "timestamp_utc": None,
                "age_sec": None,
                "expected_interval_sec": EXPECTED_SEC,
                "staleness_limit_sec": STALE_SEC,
                "timeframe": data.get("timeframe"),
                "window_candles": data.get("window_candles"),
                "source": data.get("source"),
            },
            "errors": [msg],
            "notes": "Evidence-only. No signals.",
        }

    age_sec = int((now - ts_utc).total_seconds())
    state = "OK" if age_sec <= STALE_SEC else "STALE"

    _audit({
        "ts_utc": _iso_z(now),
        "endpoint": "/status",
        "state": state,
        "age_sec": age_sec,
        "timestamp_source": ts_source,
        "timestamp_utc": _iso_z(ts_utc),
        "file": str(LATEST_FILE),
        "version": APP_VERSION,
        "pack_id": PACK_ID,
    })

    last = _load_last_state()
    last_state = (last or {}).get("state")

    if last_state != state and _can_emit_state_change(last, now):
        _audit({
            "ts_utc": _iso_z(now),
            "endpoint": "/status",
            "event": "STATE_CHANGED",
            "from": last_state,
            "to": state,
            "age_sec": age_sec,
            "timestamp_source": ts_source,
            "timestamp_utc": _iso_z(ts_utc),
            "file": str(LATEST_FILE),
            "version": APP_VERSION,
            "pack_id": PACK_ID,
        })
        last_change_ts = _iso_z(now)
    else:
        last_change_ts = (last or {}).get("last_change_ts_utc")

    _save_last_state({
        "ts_utc": _iso_z(now),
        "state": state,
        "age_sec": age_sec,
        "timestamp_source": ts_source,
        "timestamp_utc": _iso_z(ts_utc),
        "file": str(LATEST_FILE),
        "last_change_ts_utc": last_change_ts,
        "version": APP_VERSION,
        "pack_id": PACK_ID,
    })

    return {
        **_canon_header(),
        "endpoint": "/status",
        "state": state,
        "file": str(LATEST_FILE),
        "evidence": {
            "timestamp_source": ts_source,
            "timestamp_utc": _iso_z(ts_utc),
            "age_sec": age_sec,
            "expected_interval_sec": EXPECTED_SEC,
            "staleness_limit_sec": STALE_SEC,
            "timeframe": data.get("timeframe"),
            "window_candles": data.get("window_candles"),
            "source": data.get("source"),
        },
        "notes": "Evidence-only. No signals.",
        "errors": [],
    }