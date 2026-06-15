# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: E4
- [REPO_URL]: https://github.com/giangkh1908/2A202600600-KimHongGiang-Day13
- [MEMBERS]: 
  - Member A: Kim Hồng Giang | Role: Logging & PII
  - Member B: Kim Hồng Giang | Role: Tracing & Enrichment
  - Member C: Kim Hồng Giang | Role: SLO & Alerts
  - Member D: Kim Hồng Giang | Role: Load Test & Incident Injection
  - Member E: Kim Hồng Giang | Role: Dashboard & Evidence
  - Member F: Kim Hồng Giang | Role: Blueprint & Demo Lead

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: **100** /100
- [TOTAL_TRACES_COUNT]: **30** (run: `python scripts/load_test.py`)
- [PII_LEAKS_FOUND]: **0** (all PII redacted via `scrub_event` processor)

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: docs/screenshots/correlation-id.png
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: docs/screenshots/pii-redaction.png
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: docs/screenshots/trace-waterfall.png
- [TRACE_WATERFALL_EXPLANATION]: When `rag_slow` incident is enabled, the `retrieve()` span shows ~2500ms latency (vs ~150ms normal). The `generate()` span stays ~150ms. This proves the bottleneck is in retrieval, not the LLM.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: docs/screenshots/dashboard-6panels.png
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---:|---:|
| Latency P95 | < 3000ms | 28d | 152ms |
| Error Rate | < 2% | 28d | 0% |
| Cost Budget | < $2.5/day | 1d | $0.02 (10 req) |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: docs/screenshots/alerts.png
- [SAMPLE_RUNBOOK_LINK]: [docs/alerts.md#1-high-latency-p95](docs/alerts.md#1-high-latency-p95)

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: `rag_slow`
- [SYMPTOMS_OBSERVED]: `/metrics` shows P95 latency spike from 152ms → >2500ms. Langfuse traces show `retrieve()` span taking 2500ms.
- [ROOT_CAUSE_PROVED_BY]: Langfuse Trace ID: `5df8bb4fbd1c293ba0723d03f013adf4` → `retrieve()` span has duration ~2500ms with `ScheduledSleep` attribute
- [FIX_ACTION]: `python scripts/inject_incident.py --scenario rag_slow --disable`
- [PREVENTIVE_MEASURE]: Add timeout + circuit breaker for RAG retrieval; cache frequent queries

---

## 5. Individual Contributions & Evidence

### A. Kim Hồng Giang (Logging & PII)
- [TASKS_COMPLETED]: 
  - Implemented correlation ID middleware (app/middleware.py)
  - Enriched logs with user_id_hash, session_id, feature, model, env (app/main.py)
  - Added PII patterns: passport, IP address, Vietnamese address keywords (app/pii.py)
  - Activated PII scrubbing processor (app/logging_config.py)
- [EVIDENCE_LINK]: (Link to specific commit or PR)

### B. Kim Hồng Giang (Tracing & Tags)
- [TASKS_COMPLETED]: 
  - Configured Langfuse client for v3 SDK (app/tracing.py)
  - Added @observe() decorator to agent.run(), retrieve(), generate()
  - Set trace tags: ["lab", feature, model] + user_id, session_id
  - Added child spans with metadata and usage details
- [EVIDENCE_LINK]: (Link to specific commit or PR)

### C. Kim Hồng Giang (SLO & Alerts)
- [TASKS_COMPLETED]: 
  - Defined SLO targets: latency P95 < 3000ms, error rate < 2%, cost < $2.5/day, quality >= 0.75 (config/slo.yaml)
  - Created 4 alert rules with runbook links (config/alert_rules.yaml)
  - Wrote runbook for each alert (docs/alerts.md)
- [EVIDENCE_LINK]: (Link to specific commit or PR)

### D. Kim Hồng Giang (Load Test & Incident Injection)
- [TASKS_COMPLETED]: 
  - Ran load tests with sequential and concurrent requests (scripts/load_test.py)
  - Injected incidents: rag_slow, tool_fail, cost_spike (scripts/inject_incident.py)
  - Observed and documented incident impact on metrics, traces, and logs
- [EVIDENCE_LINK]: (Link to specific commit or PR)

### E. Kim Hồng Giang (Dashboard & Evidence)
- [TASKS_COMPLETED]: 
  - Built 6-panel dashboard from /metrics endpoint (docs/dashboard-spec.md)
  - Collected evidence: screenshots of traces, logs, dashboard, alerts (docs/grading-evidence.md)
  - Ran evidence_report.py for automated data collection
- [EVIDENCE_LINK]: (Link to specific commit or PR)

### F. Kim Hồng Giang (Blueprint & Demo Lead)
- [TASKS_COMPLETED]: 
  - Compiled team report in blueprint-template.md
  - Coordinated live demo and presentation
  - Ensured all passing criteria are met
- [EVIDENCE_LINK]: (Link to specific commit or PR)

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: Cost report at `GET /cost-report` shows avg cost/request. With `cost_spike` enabled, `tokens_out` x4, cost increases ~4x. Mitigation: route simple queries to cheaper model.
- [BONUS_AUDIT_LOGS]: Separate audit log at `data/audit.jsonl` — tracks user_id_hash, action, resource, status, timestamp for every chat + incident toggle.
- [BONUS_CUSTOM_METRIC]: Added `GET /cost-report` endpoint with daily cost estimate + incident impact comparison.
