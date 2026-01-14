# Multi-agent tax assistant (simulated)

An API (FastAPI or similar) that answers “tax-related” questions (with fake data) using:

Supervisor (chooses which agent acts)

RAG agent (searches documents and responds with quotes)

Policy/safety barrier agent (blocks “advice,” imposes an informative tone)

Memory + Context generator (decides what goes into the prompt: profile + summary + last turns)
