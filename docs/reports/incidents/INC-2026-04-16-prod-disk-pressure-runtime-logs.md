# INC-2026-04-16-prod-disk-pressure-runtime-logs Prod Disk Pressure From Runtime Logs And Backups

Status: mitigated
Severity: sev2
Service: production bot / Fly app `events-bot-new-wngqia`
Opened: 2026-04-16
Closed: —
Owners: operations / bot runtime
Related incidents: —
Related docs: `docs/operations/runtime-logs.md`, `docs/operations/release-governance.md`

## Summary

The production bot stopped answering Telegram because the Fly volume mounted at `/data` reached `100%` usage. Startup logging then failed with `OSError: [Errno 28] No space left on device`, so the app never reached a healthy webhook-serving state.

## User / Business Impact

- the Telegram bot stopped responding on production;
- webhook requests were refused while the machine appeared `started`;
- operator-facing CherryFlash debugging was blocked because the base bot surface was unhealthy.

## Detection

- user reported that the prod bot did not answer at all;
- Fly logs showed `OSError: [Errno 28] No space left on device`;
- `df -h /data` showed `/data` at `100%`.

## Root Cause

1. Old sqlite backup files and temporary working directories had accumulated on `/data`.
2. Runtime file logging was also enabled on the same volume (`/data/runtime_logs`).
3. Once the volume filled up, the logger failed during startup and the bot never reached a normal serving state.

## Automation Contract

### Treat as regression guard when

- changing production logging policy in `fly.toml`;
- changing runtime file logging behavior;
- adding new persistent artifacts on `/data`;
- handling emergency prod deploys on the Fly bot app.

### Affected surfaces

- `fly.toml`
- `runtime_logging.py`
- `/data` volume hygiene on Fly production

### Mandatory checks before closure or deploy

- verify `/data` free space after cleanup/deploy;
- verify `/webhook`/`/healthz` serving on prod after restart;
- keep prod logging policy and docs in sync.

## Immediate Mitigation

- removed old sqlite backups and stale temporary directories from `/data`;
- restarted the production machine after freeing space.

## Corrective Actions

- disabled `ENABLE_RUNTIME_FILE_LOGGING` in production by default;
- updated runtime logging docs to reflect the new production policy.

## Release And Closure Evidence

- deployed SHA:
- restart/deploy path:
- post-restart webhook evidence:

## Prevention

- runtime file logging should stay opt-in until there is an explicit disk budget and pruning policy for `/data`;
- old sqlite snapshots should not accumulate indefinitely on the production volume.
