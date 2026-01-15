# Multi-agent tax assistant (simulated)

An API (FastAPI or similar) that answers “tax-related” questions (with fake data) using:

Supervisor (chooses which agent acts)

RAG agent (searches documents and responds with quotes)

Policy/safety barrier agent (blocks “advice,” imposes an informative tone)

Memory + Context generator (decides what goes into the prompt: profile + summary + last turns)


START
  |
  v
Supervisor (router)
  |--(tax keywords)--> TaxInfoAgent --> END
  |
  '--(else)----------> GeneralAgent --> END

Example conversations:
1. General routing
   {"user_id":"123","message":"Hi there"}
   {"assistant_message": "I can help with general questions. Ask me anything.", "last_agent": "general"}
2. Tax routing
   {"user_id":"124","message":"How do tax refunds work?"}
   {"assistant_message": "Here is general tax information. I cannot provide personal tax advice, but I can explain rules and concepts.", "last_agent": "tax_info"}
3. Persistence
   {"messages":["user: Hi, Im 50","assistant: I can help with general questions. Ask me anything.","user: And what about deductions?","assistant: Here is general tax information. I cannot provide personal tax advice, but I can explain rules and concepts."]}

