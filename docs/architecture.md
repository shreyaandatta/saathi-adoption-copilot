# Architecture

Saathi is deliberately split so that the language model is never the source of a
fact or a product decision. Each layer has one job.

## Request flow

```
1. Customer speaks/types   →  "I have money just sitting there, what can I do?"
2. agent.handle()          →  detects intent, reads customer context
3. rules.next_best_action  →  bank's engine says what's eligible + most useful
4. journey.build_illustration → deterministic numbers (FD/SIP/term)
5. llm.rephrase (optional) →  re-voices the reply in the customer's language
6. agent offers to set it up; customer says "yes"
7. journey.stage_action    →  a staged action, blocked on consent
8. /api/confirm + OTP      →  journey.execute runs it; audit log written
```

Steps 2, 5 and 6 are where the model helps (planning + language). Steps 3, 4, 7
and 8 are deterministic code and the bank's rules — on purpose.

## Components

| File | Responsibility | Trusted with money/products? |
|------|----------------|------------------------------|
| `agent.py` | Conversation orchestration, intent, planning | No |
| `llm.py` | Optional Claude re-voicing (language only) | No |
| `rules.py` | Eligibility + suitability (source of truth) | Decides eligibility only |
| `journey.py` | Illustrations, staged actions, consent gate | Computes numbers, gates execution |
| `store.py` | Mock bank data, session state, audit log | Holds data |
| `app.py` | HTTP API + serves the UI | — |

## Guardrails (built in, not bolted on)

- **Education, not advice** — the model explains and illustrates; suitability comes
  from `rules.py`. This keeps it clear of investment-advice / mis-selling exposure.
- **Grounded numbers** — every figure comes from `journey.py` formulas, never the model.
- **Consent gate** — money-moving actions are staged and require an OTP (`journey.execute`).
- **Audit trail** — every inbound message, staged action, consent event and execution
  is logged per customer (`store.log`), ready for compliance review.

## API

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Chat UI |
| GET | `/api/customers` | List demo customers |
| GET | `/api/customer/{id}` | Full customer profile |
| POST | `/api/chat` | `{customer_id, message}` → `{reply, proposal?}` |
| POST | `/api/confirm` | `{customer_id, otp}` → booking result |
| GET | `/api/audit/{id}` | Audit trail for a customer |

## What a production build changes

- Mock JSON → the bank's real account APIs and product-rules engine
- Template/Claude text → full vernacular **voice** in and out (Bhashini / Sarvam)
- The mock `stage_action` → a journey executor over real app deep-links
- Fixed demo OTP → real OTP / biometric consent
- In-memory audit → the bank's system of record
