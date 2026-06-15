# Mock Debug Q&A — Oral/Written Debugging Questions

Prepare answers for these questions. Instructors may ask during the demo.

## Logging & Correlation ID

**Q1:** How does the correlation ID propagate from middleware to logs?
**A:** Middleware (`app/middleware.py`) generates/reads `x-request-id`, binds it to `structlog.contextvars` via `bind_contextvars(correlation_id=...)`. The `merge_contextvars` processor in structlog injects it into every log event automatically.

**Q2:** What happens if you forget `clear_contextvars()` at the start of each request?
**A:** Context variables from the previous request leak into the next, causing wrong `correlation_id` and `user_id_hash` in logs — hard to debug.

## PII Scrubbing

**Q3:** How does the PII scrubber work? Give an example regex.
**A:** `app/pii.py` defines patterns + replacement. For example:
- Email: `[\w\.-]+@[\w\.-]+\.\w+` → `[REDACTED_EMAIL]`
- Phone VN: `(?:\+84|0)[ \.-]?\d{3}[ \.-]?\d{3}[ \.-]?\d{3,4}` → `[REDACTED_PHONE_VN]`
- Credit card: `\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b` → `[REDACTED_CREDIT_CARD]`

**Q4:** Why is the scrubber placed BEFORE `JSONRenderer` in the processor chain?
**A:** So PII is removed from the event dict before serialization. If placed after, the raw payload (with PII) would already be serialized.

## Tracing

**Q5:** What is the difference between `@observe()` and `@observe(as_type="generation")`?
**A:** `@observe()` creates a generic span. `@observe(as_type="generation")` creates a generation span with extra LLM metadata (model, usage tokens, cost).

**Q6:** How do child spans relate to the parent trace?
**A:** `@observe()` on nested functions automatically creates parent-child relationships via OTel context propagation. The trace waterfall shows: `agent.run()` → `retrieve()` + `generate()`.

## Metrics

**Q7:** How is P95 latency calculated?
**A:** `app/metrics.py`: sort all latencies, pick the value at index `round((95/100) * len(values) + 0.5) - 1`. This gives the latency below which 95% of requests fall.

**Q8:** The `/metrics` endpoint resets on server restart. Why is this a problem?
**A:** Metrics are in-memory (Python lists). A restart wipes them. For production, use a time-series DB (Prometheus, etc.) with persistent storage.

## SLO & Alerts

**Q9:** What is the difference between an SLO and an alert?
**A:** SLO defines the target (e.g., "P95 < 3000ms 99% of the time"). An alert fires when the burn rate threatens the SLO (e.g., "P95 > 5000ms for 30m").

**Q10:** How would you debug a `rag_slow` incident using Metrics → Traces → Logs?
**A:**
1. **Metrics**: `/metrics` shows latency spike (P95 > 3000ms)
2. **Traces**: Langfuse waterfall shows `retrieve()` span taking 2500ms
3. **Logs**: `data/logs.jsonl` shows `service="rag"` with high latency for `rag_slow` requests

## Incident Response

**Q11:** Walk through the steps to diagnose and fix `tool_fail`.
**A:**
1. Check `/metrics` for `error_breakdown: {"RuntimeError": N}`
2. Open Langfuse → find failed trace → see `retrieve()` span with error
3. Logs show `"error_type": "RuntimeError"` with `"Vector store timeout"`
4. Fix: `python scripts/inject_incident.py --scenario tool_fail --disable`

**Q12:** How do you verify the fix worked?
**A:** Run `python scripts/load_test.py` → check `/metrics` (error count stops increasing) → check Langfuse (no new error spans).
