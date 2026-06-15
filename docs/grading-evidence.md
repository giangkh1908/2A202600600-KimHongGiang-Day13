# Evidence Collection Sheet

## How to collect

### 1. Start the app + send requests
```bash
uvicorn app.main:app --reload            # Terminal 1
python scripts/load_test.py              # Terminal 2
python scripts/evidence_report.py        # Terminal 3
```

### 2. Check validation
```bash
python scripts/validate_logs.py
```

## Required screenshots

| # | Screenshot | How to capture | Who |
|---|-----------|----------------|-----|
| 1 | Langfuse trace list (>= 10 traces) | Langfuse UI → Traces tab | B |
| 2 | One full trace waterfall (3 spans) | Click a trace → show waterfall | B |
| 3 | JSON log with correlation_id | `data/logs.jsonl` → find `correlation_id` field | A |
| 4 | Log line with PII redaction | Same file → find `[REDACTED_EMAIL]` or `[REDACTED_PHONE_VN]` | A |
| 5 | Dashboard with 6 panels | `GET /metrics` response or Grafana | E |
| 6 | Alert rules with runbook link | `config/alert_rules.yaml` + `docs/alerts.md` | C |

## Optional screenshots
- Incident before/after: enable `rag_slow`, run load_test, note latency change in trace
- Cost comparison: enable `cost_spike`, compare tokens_out before/after
- Auto-instrumentation: screenshot of Langfuse auto-instrumentation config
