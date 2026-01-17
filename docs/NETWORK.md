# MarginPlus --- Network & Firewall Notes (Production)

This document defines the **network exposure and firewall model** for
MarginPlus MVP v2.0.

The goal is **minimum attack surface with clear operational access**.

------------------------------------------------------------------------

## 📐 Scope

-   Project: MarginPlus MVP v2.0
-   Runtime server: `tv-webhook-phase2`
-   Mode: Production / Read-only core
-   Status: LOCKED

------------------------------------------------------------------------

## 🔒 Inbound Rules

### SSH (TCP/22)

-   Access model: **Bastion / Jump Host**

-   Allowlist only (no public SSH)

-   Example allowed source:

        ods-authority (single IP /32)

Properties: - Key-based authentication only - Password login disabled -
Root access via SSH key

------------------------------------------------------------------------

### HTTP / HTTPS

-   Exposed via reverse proxy (Caddy)
-   Purpose:
    -   Public read-only access (if required)
    -   Redirect HTTP → HTTPS

Notes: - Health endpoint `/health` may return `308` (redirect) - Backend
health runs on local port only

------------------------------------------------------------------------

## 🩺 Local-only Ports

The following ports are **not exposed publicly**:

    127.0.0.1:8090   # Backend health & API

Access: - Local process only - Used for smoke test and diagnostics

------------------------------------------------------------------------

## 🌐 Outbound Rules

Outbound traffic is allowed for: - Market data fetch (e.g., exchange
APIs) - System updates - Dependency downloads

No inbound dependency callbacks are required.

------------------------------------------------------------------------

## 🧱 Security Model Summary

-   Single controlled SSH entry point
-   No wide CIDR ranges
-   No public admin interfaces
-   Runtime server holds no Git repository or secrets

Operational principle: \> **Establish SSH trust first, then lock the
firewall**

------------------------------------------------------------------------

## ⚠️ Operational Warnings

-   Do NOT open SSH to `0.0.0.0/0`
-   Do NOT rely on cloud provider web console as a permanent access path
-   Any firewall change must be verified with SSH access before locking

------------------------------------------------------------------------

## 📄 Change Policy

This document is **LOCKED** for MVP v2.0.

Any change requires: - Explicit approval - Documentation update -
Rollback plan

------------------------------------------------------------------------

## 📄 License

MIT
