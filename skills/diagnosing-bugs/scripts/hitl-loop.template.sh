#!/usr/bin/env bash
# Human-in-the-loop reproduction loop.
# Copy this file, edit the steps below, and run it.
# The agent runs the script (exec with pty=true) and BOTH agent and user must
# share that same terminal. If they don't (e.g. a chat-only deployment),
# don't use this script — ask the questions directly in the conversation.
#
# Usage:
#   bash hitl-loop.template.sh
#
# Two helpers:
#   step "<instruction>"          → show instruction, wait for Enter
#   capture VAR "<question>"      → show question, read response into VAR
#
# At the end, captured values are printed as KEY=VALUE for the agent to parse.
#
# `capture` prints its value back to the terminal, where the agent reads it,
# so capture observations, and leave signing in to the user as a `step`.

set -euo pipefail

# Non-interactive run (no pty / stdin redirected) would die on the first `read`
# under `set -e`, silently dropping every captured value. Fail loudly instead.
if [ ! -t 0 ]; then
  printf 'ERROR: 需要交互式 TTY。\n' >&2
  printf '  agent 侧：exec 必须带 pty=true\n' >&2
  printf '  用户在聊天里看不到该终端时：改用「agent 逐条提问」形态，不要用本脚本\n' >&2
  exit 2
fi

step() {
  printf '\n>>> %s\n' "$1"
  read -r -p "    [Enter when done] " _
}

capture() {
  local var="$1" question="$2" answer
  printf '\n>>> %s\n' "$question"
  read -r -p "    > " answer
  printf -v "$var" '%s' "$answer"
}

# --- edit below ---------------------------------------------------------

step "Open the app at http://localhost:3000 and sign in."

capture ERRORED "Click the 'Export' button. Did it throw an error? (y/n)"

capture ERROR_MSG "Paste the error message (or 'none'):"

# --- edit above ---------------------------------------------------------

printf '\n--- Captured ---\n'
printf 'ERRORED=%s\n' "$ERRORED"
printf 'ERROR_MSG=%s\n' "$ERROR_MSG"
