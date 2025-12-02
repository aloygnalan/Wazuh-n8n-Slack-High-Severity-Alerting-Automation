# 🧩 Wazuh → n8n → Slack High-Severity Alert Automation

## 🔍 Project Overview

This project builds a **real-time SOC alerting pipeline** that connects:

> 🛡️ **Wazuh → n8n → Slack (#soc-alerts channel)**

Whenever Wazuh detects a **high-severity attack** (e.g., brute force, authentication failures, malware activity),
the alert is forwarded to **n8n**, processed, enriched, and instantly sent to the SOC team via **Slack**.

This replaces outdated email alerting and provides:

* Faster response
* Real-time visibility
* Clean & structured notifications
* Easy integration with other SOAR logic

---

## 🧩 Key Features

### ✔ Real-time alert pipeline

Wazuh instantly triggers n8n whenever a high-severity rule fires.

### ✔ Slack-based SOC notifications

Alerts appear immediately in:

```
#soc-alerts
```

### ✔ Full alert summary

Includes:

* Severity
* Rule ID
* Description
* Agent name + IP
* Attacker IP
* Timestamp
* Full Log

### ✔ Extendable for SOAR automation

You can plug in:

* GeoIP
* VirusTotal enrichment
* Auto-block attacker IP
* Ticket creation (TheHive, JIRA)

### ✔ Clean, production-grade integration scripts

---

## 🧱 Architecture

<img width="795" height="248" alt="Screenshot From 2025-12-02 16-44-36" src="https://github.com/user-attachments/assets/3079c15c-40c1-4cb5-b3e6-a96838797d95" />


# Output:

<img width="1896" height="859" alt="Screenshot From 2025-12-02 16-45-34" src="https://github.com/user-attachments/assets/bda3d30a-4402-4ee7-b441-1c270b440e2d" />

---

## ⚙️ Workflow Summary

| Step | Component                     | Description                               |
| ---- | ----------------------------- | ----------------------------------------- |
| 1️⃣  | **Wazuh Rule**                | Detects high-severity events.             |
| 2️⃣  | **Custom Integration Script** | Sends alert payload to n8n Webhook.       |
| 3️⃣  | **n8n Webhook Node**          | Receives the JSON alert.                  |
| 4️⃣  | **IF Node (Severity ≥ 7)**    | Filters only high-severity alerts.        |
| 5️⃣  | **Slack HTTP Request Node**   | Sends formatted message to Slack channel. |
---

# ⚙️ Setup Guide

# 1️⃣ Wazuh Integration

Copy scripts to integration directory:

```bash
cp custom-n8n-highsev /var/ossec/integrations/
cp custom-n8n-highsev.py /var/ossec/integrations/
chmod +x /var/ossec/integrations/custom-n8n-highsev
chmod +x /var/ossec/integrations/custom-n8n-highsev.py
chown root:wazuh /var/ossec/integrations/custom-n8n-highsev
chown root:wazuh /var/ossec/integrations/custom-n8n-highsev.py
```

Add this to `/var/ossec/etc/ossec.conf`:

```xml
<integration>
  <name>custom-n8n-highsev</name>
  <hook_url>http://localhost:5678/webhook-test/wazuh-highseverity</hook_url>
  <alert_format>json</alert_format>
</integration>
```

Restart Wazuh:

```bash
systemctl restart wazuh-manager
```
---

# 2️⃣ n8n Webhook Node

* Method: **POST**
* URL:

  ```
  http://localhost:5678/webhook/wazuh-highseverity
  ```

---

# 3️⃣ IF Node (Filter High Severity)

Condition:

```
{{ $json.body.severity }} >= 7
```

---

# 4️⃣ Slack Node (HTTP Request)

### Body Content Type:

```
JSON
```

### Body (Using JSON):

```json
{
  "text": "🚨 Wazuh High Severity Alert\n\nLevel: {{ $json.body.severity }}\nRule ID: {{ $json.body.rule_id }}\nDescription: {{ $json.body.description }}\n\nAgent: {{ $json.body.agent_name }} ({{ $json.body.full_alert.agent.ip }})\nAttacker IP: {{ $json.body.full_alert.data.srcip }}\nTime: {{ $json.body.full_alert.timestamp }}\n\nFull Log:\n{{ $json.body.full_alert.full_log }}"
}
```

### Headers:

| Name         | Value            |
| ------------ | ---------------- |
| Content-Type | application/json |

---
