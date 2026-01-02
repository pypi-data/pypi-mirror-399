#!/usr/bin/env bash
# Native GNOME notification via D‑Bus

trap 'echo -e "\nStrict Mode Error: A command has failed. Exiting the script.\n  Line was ($0:$LINENO):\n    $(sed -n "${LINENO}p" "$0" 2>/dev/null || true)"; exit 3' ERR
set -Eeuo pipefail

SUMMARY="$1"
BODY="$2"
ICON="$3" # e.g. 'dialog-information'

APP_NAME="open-latest-screenshot"
ICON="$ICON"  # any icon name in /usr/share/icons
SUMMARY="$SUMMARY"
BODY="$BODY"
EXPIRE_MS=5000  # 0 = never expires

# Build the D‑Bus call
gdbus call \
  --session \
  --dest org.freedesktop.Notifications \
  --object-path /org/freedesktop/Notifications \
  --method org.freedesktop.Notifications.Notify \
  "$APP_NAME" 0 "$ICON" "$SUMMARY" "$BODY" [] {} $EXPIRE_MS
