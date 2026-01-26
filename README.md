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
   {"user_id":"42","message":"Hi, I'm 50"}
   {
      "assistant_message": "I can help with general questions. Ask me anything.",
      "last_agent": "general"
   }
   {"user_id":"42","message":"And what about deductions?"}
   {
      "assistant_message": "Here is general tax information. I cannot provide personal tax advice, but I can explain rules and concepts.",
      "last_agent": "tax_info"
   }
   {
      "messages": [
         "user: Hi, Im 42",
         "assistant: I can help with general questions. Ask me anything.",
         "user: And what about deductions?",
         "assistant: Here is general tax information. I cannot provide personal tax advice, but I can explain rules and concepts."
      ]
   }


Examples with different prompts and routes
1. Same question, different style
{"user_id":"400","message":"How do deductions work in Germany?","prompt_version":"v1"}
{
  "assistant_message": "Here is general tax information. Deductions typically reduce your taxable income, but eligibility depends on your country and the specific expense type. I cannot provide personal tax advice, but I can explain general rules and concepts.",
  "last_agent": "tax_info",
  "debug_prompt": "SYSTEM:\n1. Be accurate and truthful. If you are not sure, say so and ask a clarifying question.\n2. No personal tax advice. Provide general information only.\n3. Ask for missing context. If the user’s question depends on details, ask exactly one clarifying question.\n4. Be clear and structured. Use short paragraphs or bullet points when helpful.\n5. Respect privacy. Do not request or expose sensitive personal data unnecessarily.\n\nOBJECTIVE:\nProvide general tax information only. Do not give personal tax/legal advice. If details are missing, ask exactly one clarifying question.\n\nHISTORY:\nuser: How do deductions work in Germany?\nassistant: Here is general tax information. Deductions typically reduce your taxable income, but eligibility depends on your country and the specific expense type. I cannot provide personal tax advice, but I can explain general rules and concepts.\nuser: How do deductions work in Germany?"
}

{
  "assistant_message": "Deductions generally reduce taxable income if specific conditions are met. Rules vary by country and deduction type.",
  "last_agent": "tax_info",
  "debug_prompt": "SYSTEM:\n1. Do not hallucinate. Never invent facts, numbers, laws, or sources. If evidence is missing, say what is missing.\n2. Strictly informational. Do not recommend actions (“you should…”, “I suggest…”). Rephrase into neutral information.\n3. One-question policy. If clarification is needed, ask exactly one question and stop.\n4. Concise output. Maximum 5 sentences unless the user explicitly asks for more detail.\n5. Evidence-aware. If evidence is provided, cite it. If no evidence is provided, state that you are answering at a high level.\n\nOBJECTIVE:\nProvide general tax information only. Do not give personal tax/legal advice. If details are missing, ask exactly one clarifying question.\n\nHISTORY:\nuser: How do deductions work in Germany?\nassistant: Deductions generally reduce taxable income if specific conditions are met. Rules vary by country and deduction type.\nuser: How do deductions work in Germany?"
}