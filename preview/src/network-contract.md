# Network feature boundary

The hosted page uses a session-only demo adapter. It does not inspect, scan or modify the visitor's network. It is not a real-time native provider. Its periodic values are a labelled deterministic replay. Demo passphrases are format-checked only, never router-authenticated, stored, logged or transmitted.

The UI now covers: access-point selection, explicit scan/radio control, saved/security state, signal/link/band/channel/BSSID, IP/gateway/DNS/IPv6/MAC, throughput/session counters, demo diagnostics, connection/cancellation, passphrase visibility, disconnect/forget confirmation, IP/DNS/MTU/privacy/autoconnect/metering edits, review/apply and timed keep/revert. Form drafts are not rebuilt on every metric tick. Sampling runs only while the network panel is open and visible, at full/balanced/lite 1/2/5 seconds.

## Native implementation still required

Use the PRD's single `ttoxd` network provider for read state/counters, with its versioned `ok|empty|error` snapshots, timeouts and subscriptions. Both KDE and XFCE should use the same capability-detected NetworkManager integration; do not add a separate root metrics daemon or browser-accessible privileged HTTP server.

Connection/profile actions belong behind a small native adapter using NetworkManager's D-Bus API, validated device/profile IDs and an explicit action allowlist. No arbitrary shell command interpolation. Privileged actions use the platform's policy/polkit authorization; the UI must never collect a sudo/admin password.

Wi-Fi passphrases are distinct from system authorization. The existing desktop NetworkManager secret agent/keyring should handle them. If a custom native prompt is required, register an appropriately scoped secret agent and keep secret values out of argv, config, metrics, logs and browser storage. The user must explicitly choose any durable keyring storage. The browser demo's passphrase form is not this native integration.

Before applying potentially disconnecting settings, use a NetworkManager device checkpoint with a rollback timeout. Native keep destroys the checkpoint; timeout/failure rolls back independently of the UI process. The demo models review and a 15-second confirmation but does not implement a native checkpoint. Native persistent settings and rollback must also fit installer/state-manifest requirements.

Read and modify capabilities must be checked on the target host. Missing NetworkManager, interfaces, Wi-Fi hardware, permissions and saved secrets need real empty/error states. Privilege-denied and authentication-failure outcomes must remain separate from bad field validation. Native mutation controls must reconcile the PRD's original two-click policy with the later requested review/password flows.

## Required native verification

Real AP scan/connect/disconnect, wrong passphrase, denied policy, adapter missing, multiple interfaces, Wi-Fi in a VM without hardware, device loss, profile restore, daemon failure, checkpoint rollback and secret redaction must be tested on actual target desktops. The browser/model tests are not substitutes.
