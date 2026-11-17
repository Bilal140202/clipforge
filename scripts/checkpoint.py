#!/usr/bin/env python3
"""ClipForge checkpoint manager (addendum section 5).

Honest scope: this runtime is a disposable sandbox — background processes
die when the agent turn ends and the filesystem is not guaranteed between
sessions. GitHub is the durable store. This tool reports measured local
state (no fake health), verifies remote sync, and with --note appends a
timestamped checkpoint line to WORKLOG.md so a fresh session can resume
from repository state alone.

Usage:
  python scripts/checkpoint.py                 # health JSON to stdout
  python scripts/checkpoint.py --note "..."    # also record a checkpoint
"""
import argparse
import datetime
import json
import subprocess


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--note", default="", help="checkpoint note for WORKLOG")
    args = ap.parse_args()

    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
    head = run(["git", "rev-parse", "HEAD"]).stdout.strip()[:12]
    status = run(["git", "status", "--porcelain"]).stdout
    dirty = len([l for l in status.splitlines() if l.strip()])
    sb = run(["git", "status", "-sb"]).stdout.splitlines()[0]
    ahead = int(sb.split("[")[1].split("]")[0].split(",")[0].strip()
                .replace("ahead ", "")) if "[" in sb else 0
    behind = int(sb.split("[")[1].split("]")[0].split(",")[1].strip()
                 .replace("behind ", "")) if "[" in sb and "," in sb else 0
    fetch = run(["git", "fetch", "origin"])
    sb = run(["git", "status", "-sb"]).stdout.splitlines()[0]
    synced = "behind" not in sb and ahead == 0
    remote_head = run(["git", "ls-remote", "origin", branch]).stdout[:12]
    health = {
        "checkpoint_utc": datetime.datetime.now(
            datetime.timezone.utc).isoformat(timespec="seconds"),
        "branch": branch,
        "head": head,
        "remote_head": remote_head,
        "remote_synced": synced and not fetch.returncode,
        "dirty_files": dirty,
        "unpushed_commits": ahead,
        "behind_remote": behind,
        "healthy": dirty == 0 and synced and fetch.returncode == 0,
        "note": "filesystem+processes are disposable; GitHub is durable",
    }
    print(json.dumps(health, indent=2))
    if args.note:
        entry = (f"\n### Checkpoint {health['checkpoint_utc']} — {args.note}"
                 f"\n- branch `{branch}` head `{head}` remote_head "
                 f"`{remote_head}` synced={health['remote_synced']} "
                 f"dirty={dirty}\n")
        with open("WORKLOG.md", "a") as f:
            f.write(entry)
        print("checkpoint recorded in WORKLOG.md")
        if dirty:
            print("WARNING: dirty files present — commit before ending "
                  "the session (addendum section 11).", flush=True)


if __name__ == "__main__":
    main()
