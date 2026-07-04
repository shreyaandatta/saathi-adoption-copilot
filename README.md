# Saathi — Agentic Adoption Copilot

> A banking helper that doesn't just answer questions — it does the whole journey for you, in your own language, and stops for your consent before any money moves.

Built for **Global Fintech Fest 2026 · SBI Hackathon** — Pillar 02, *Digital Adoption*.

---

## The problem

A bank the size of SBI opens accounts at massive scale, but most customers only ever check a balance or send money on UPI. They never start an FD, a SIP, or buy insurance — not for lack of interest, but because the journeys are long, in English, and full of jargon. The gap between *having an account* and *using its products* is the biggest untapped pool in retail banking.

## What Saathi does

1. **Spots the next step** — notices something useful from the customer's own activity (e.g. money sitting idle in savings).
2. **Explains it simply** — plain language, a clearly-marked illustration. Education, not advice.
3. **Does the journey** — walks through the whole booking itself and pauses only for consent.

It's not a chatbot bolted onto the app. It's a copilot that removes the friction that kills adoption.

## What's in this prototype

This is a small but **fully working** slice you can run in a minute:

- A conversational agent that detects intent and drives a multi-turn journey
- A **product-rules engine** that is the source of truth for what a customer may be offered
- **Deterministic illustrations** (FD maturity, SIP growth, term premium) — the model never invents a number
- A **consent gate**: anything that moves money is staged and only executes after an OTP
- A running **audit trail** of every step
- A mobile-style chat UI

### The two design decisions that matter

- **Education, not advice.** Saathi explains and illustrates; *suitability* comes from the bank's own compliant rules engine (`backend/rules.py`), not the model. This sidesteps the mis-selling / RIA problem.
- **Human consent on money.** Autonomy for the friction, a firm stop for funds. See the consent gate in `backend/journey.py`.

## Run it

```bash
pip install -r requirements.txt
uvicorn backend.app:app --reload
# open http://localhost:8000
```

Then pick a customer and try: *"I have some money just sitting there, what can I do?"* → say **yes** → confirm with demo OTP **1234**.

### Optional: turn on the Claude layer

Saathi runs fully without any API key using grounded template replies. To enable the natural-language / vernacular re-voicing:

```bash
cp .env.example .env      # then paste your key
export ANTHROPIC_API_KEY=sk-ant-...
```

With a key set, replies are re-voiced by Claude (Haiku 4.5) in the customer's language — but Claude is only allowed to *rephrase*; every number and product choice still comes from the rules/journey layers.

## Architecture

```
Customer (chat UI)
      │
   agent.py  ── orchestrates the conversation, plans the steps
      │
      ├── rules.py     → what is this customer eligible for?   (source of truth)
      ├── journey.py   → illustrations + staged actions + consent gate (real numbers)
      ├── llm.py       → optional Claude re-voicing in the customer's language
      └── store.py     → mock bank data + session state + audit log
```

The rule running through all of it: **Saathi is trusted to talk, plan, and remove friction — never to decide products or move money on its own.**

See [`docs/architecture.md`](docs/architecture.md) for detail, and [`docs/`](docs/) for the idea deck.

## Project layout

```
saathi/
├── backend/          FastAPI app + agent, rules, journey, llm, store
├── frontend/         single-page chat UI
├── data/             mock customers + products (the "all the data")
├── docs/             architecture notes + idea deck
└── requirements.txt
```

## Roadmap (beyond the prototype)

- Real vernacular voice in/out (Bhashini / Sarvam) for spoken journeys
- Journey executor over real YONO deep-links instead of the mock
- Biometric consent + hand-off to the bank's live rules and KYC systems
- Adoption analytics: dormant-activation rate, journey completion, tap-count saved

## Disclaimer

Prototype for a hackathon. Mock data only, no real accounts or money. Interest/return figures are illustrative and not financial advice.

## License

MIT — see [LICENSE](LICENSE).
