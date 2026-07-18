#!/usr/bin/env bash
# Dumb, deterministic, no-LLM watcher for the unattended Codex $goal run on
# this repo. Polls git log + scratchpad.md/HANDOFF.md every 15 minutes and
# sends a plain-text summary via `hermes send` (no gateway, no agent loop,
# no token cost). Intentionally has zero reasoning in it — it can't forget,
# hallucinate, or get distracted, unlike baking this into the agent's own
# loop would risk.
set -euo pipefail

REPO="/home/tangoren/projects/braille-greeting-cards"
STATE_FILE="$REPO/.watcher_last_sha"
INTERVAL=900  # 15 minutes
TARGET="telegram"

cd "$REPO"

send() {
    hermes send --to "$TARGET" --subject "[BrailleCard]" "$1" --quiet
}

# Optional: pass the codex process's PID as $1 so a dead process can be
# distinguished from a slow-but-alive one. If omitted, silence detection
# still works via consecutive-quiet-cycle escalation below.
CODEX_PID="${1:-}"

last_sha=""
[ -f "$STATE_FILE" ] && last_sha=$(cat "$STATE_FILE")
quiet_cycles=0

send "Watcher started. Polling every 15 min. Will report new commits, blockers, and silence — and will escalate if it looks stalled (e.g. a usage-limit hit, which fails Codex instantly with no partial work or error surfaced elsewhere)."

while true; do
    sleep "$INTERVAL"

    current_sha=$(git rev-parse HEAD 2>/dev/null || echo "")
    new_commits=""
    if [ -n "$current_sha" ] && [ "$current_sha" != "$last_sha" ]; then
        if [ -n "$last_sha" ]; then
            new_commits=$(git log --oneline "$last_sha..$current_sha" 2>/dev/null || echo "")
        else
            new_commits=$(git log --oneline -5 2>/dev/null || echo "")
        fi
        echo "$current_sha" > "$STATE_FILE"
        last_sha="$current_sha"
    fi

    blocker=""
    if [ -f "$REPO/scratchpad.md" ]; then
        blocker=$(grep -iE "blocker|stopping|stopped" "$REPO/scratchpad.md" 2>/dev/null | tail -3 || true)
    fi

    proc_dead=""
    if [ -n "$CODEX_PID" ] && ! kill -0 "$CODEX_PID" 2>/dev/null; then
        proc_dead="1"
    fi

    if [ -n "$new_commits" ]; then
        quiet_cycles=0
        msg="New commits:
$new_commits"
        [ -n "$blocker" ] && msg="$msg

scratchpad.md mentions:
$blocker"
        send "$msg"
    elif [ -n "$proc_dead" ]; then
        send "ALERT: the Codex process (PID $CODEX_PID) is no longer running, but no HANDOFF.md was written and no new commits landed. This looks like an unclean stop — possibly a usage-limit hit (fails instantly, no error surfaced elsewhere). Check manually."
        break
    elif [ -n "$blocker" ]; then
        quiet_cycles=0
        send "No new commits, but scratchpad.md mentions:
$blocker"
    else
        quiet_cycles=$((quiet_cycles + 1))
        if [ "$quiet_cycles" -ge 2 ]; then
            send "ALERT: no new commits, no scratchpad blocker note, for $((quiet_cycles * 15)) minutes (HEAD still $current_sha). Longer than a single iteration should normally take — worth checking whether the run is still actually working or silently stopped."
        else
            send "No new activity in the last 15 min (HEAD still $current_sha)."
        fi
    fi

    if [ -f "$REPO/HANDOFF.md" ]; then
        send "HANDOFF.md now exists — likely means the run finished or hit a stopping condition. Check it: $REPO/HANDOFF.md"
        break
    fi
done
