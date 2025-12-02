#!/usr/bin/env python3
# ==========================================================
# Custom Wazuh \u2192 n8n Integration for High Severity Alerts
# Sends alert JSON (level >= 7) to n8n Webhook via POST
# ==========================================================

import sys
import json
import requests

LOG_FILE = "/var/ossec/logs/integrations.log"

def log_message(msg):
    """Write debug info to Wazuh's integration log."""
    with open(LOG_FILE, "a") as log:
        log.write(f"[custom-n8n-highsev] {msg}\n")

def main():
    # Wazuh passes: <alert_file> <user> <hook_url>
    if len(sys.argv) < 4:
        log_message("\u274c Missing arguments. Usage: custom-n8n-highsev.py <alert_file> <user> <hook_url>")
        sys.exit(1)

    alert_file = sys.argv[1]
    hook_url   = sys.argv[3]

    # -------------------------------------
    # Read single alert JSON from Wazuh
    # -------------------------------------
    try:
        with open(alert_file, "r") as f:
            content = f.read().strip()

            if not content:
                log_message("\u26a0\ufe0f Alert file empty \u2014 skipping.")
                return

            # Handle multi-line or appended logs
            try:
                alert = json.loads(content)
            except json.JSONDecodeError:
                # Take only last line if multiple lines present
                lines = content.splitlines()
                alert = json.loads(lines[-1])

    except Exception as e:
        log_message(f"Error reading alert file: {e}")
        return

    # -------------------------------------
    # Extract rule info & filter by severity
    # -------------------------------------
    rule = alert.get("rule", {})
    level = rule.get("level", 0)

    if level < 7:
        log_message(f"Skipping low-severity alert (level={level}).")
        return

    # -------------------------------------
    # Prepare payload for n8n
    # -------------------------------------
    agent = alert.get("agent", {})
    payload = {
        "severity": level,
        "rule_id": rule.get("id", ""),
        "description": rule.get("description", ""),
        "timestamp": alert.get("timestamp", ""),
        "agent_name": agent.get("name", ""),
        "agent_id": agent.get("id", ""),
        "location": alert.get("location", ""),
        "full_alert": alert
    }

    # -------------------------------------
    # Send to n8n webhook
    # -------------------------------------
    try:
        resp = requests.post(hook_url, json=payload, timeout=10)

        if resp.status_code == 200:
            log_message(f"\u2714\ufe0f High Severity Alert Sent (level={level}) \u2192 {hook_url}")
        else:
            log_message(f"\u26a0\ufe0f HTTP {resp.status_code} from n8n: {resp.text}")

    except Exception as e:
        log_message(f"Error sending alert to n8n: {e}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_message(f"Unexpected error: {e}")
        sys.exit(1)

