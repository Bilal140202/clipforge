# RECOVERY.md — session health, checkpointing, and recovery (honest inventory)

Written 2026-11-17 per the owner's persistence addendum (see
`docs/GOVERNANCE.md`). Rule: **document what the runtime actually supports,
never claim a mechanism that was not implemented and observed.**

## Measured runtime capabilities (verified 2026-11-17)

| Capability | Available? | Evidence |
| --- | --- | --- |
| Filesystem persistence | within a session, yes; across sessions, NOT guaranteed | sandbox recycles between agent turns; /home/z/my-project survived within one session |
| Background processes | only while the agent turn is running | nohup transcription survived across tool calls in-turn; killed at turn end |
| Process supervisors / watchdogs | NO | no supervisor exists in the sandbox |
| Cron / scheduling | platform-managed agent scheduling only | the agent harness offers cron for agent turns; NOT usable as a project-level watchdog |
| GitHub API | YES | token verified: `GET /user` = Bilal140202, `.permissions.push=true` |
| GitHub Actions | YES | green run `00e3155` on ubuntu-latest (CI evidence) |
| Auto session resume | NO | no resume hook exists; recovery = the documented startup protocol |

Consequence: **GitHub is the only durable store.** Issues are the task
ledger; commits are durable progress; WORKLOG.md is the execution history.

## Checkpoint manager

`scripts/checkpoint.py` (implemented + executed):
- prints machine-readable health: branch, HEAD, remote HEAD, sync state,
  dirty-file count, unpushed commits;
- `--note "..."` appends a timestamped checkpoint line to WORKLOG.md;
- healthy = clean tree + synced with origin (measured, not asserted).

Checkpoint after: each completed task (before closing its issue), each
green test cycle, before ending a session, and whenever a restart seems
likely. A checkpoint is only durable once the commit is pushed and
`remote_synced: true` is observed.

## Recovery procedure (a fresh session follows AGENTS.md)

1. Verify GitHub identity + repo permissions (AGENTS.md "Verify before
   work").
2. `git fetch`; compare local vs origin; if diverged, reconcile before
   editing — never push a stale copy over newer remote commits.
3. Read WORKLOG.md checkpoints (tail) → latest issue state → PLAN.md.
4. Confirm toolchain (`python -m pytest tests/ -q`, ffmpeg present).
5. Resume the highest-priority open issue from its "Completion evidence"
   section.

## Interruption safety rules (addendum §5.4)

- Bounded retries: max 3 attempts per operation, then record the blocker
  in the active issue and move to independent work.
- Idempotent operations: issue creation, checkpoint notes, and pushes are
  checked against remote state first to avoid duplicates.
- No duplicate workers: one active issue per session; stale-task detection
  = issue state + CI status, not imaginary heartbeats.
- Stop and document when a human decision or new credentials are required.
