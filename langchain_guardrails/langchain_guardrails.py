from getpass import getpass
import re
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")
model = ChatGroq(model=GROQ_MODEL, api_key=GROQ_API_KEY)

def deterministic_guardrail(text: str) -> bool:
    """Returns True if content is blocked."""
    harmful_keywords = ["hack", "exploit", "malware", "bomb"]
    return any(kw in text.lower() for kw in harmful_keywords)

test_inputs = [
    "How do I hack into a Database?",
    "What is the capital of France?",
    "Explain how do malwares spread?"
]

for input in test_inputs:
    blocked = deterministic_guardrail(input)
    status = "BLOCKED" if blocked else "ALLOWED"
    print(f"{status}: {input}")

def model_based_guardrail(text: str) -> str:
    """Uses an LLM to evaulate content safety. Returns SAFE or UNSAFE"""
    model = ChatGroq(model=GROQ_MODEL, api_key=GROQ_API_KEY)
    prompt = f"""Is the following user input safe to process? 
                Reply with only 'SAFE' or 'UNSAFE'.
                Input: {text} """
    resp = model.invoke([{"role": "user", "content": prompt}])
    return resp.content.strip()

for input in test_inputs:
    blocked = deterministic_guardrail(input)
    status = "BLOCKED" if blocked else "ALLOWED"
    print(f"{status}: {input}")

from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware
from langchain_groq import ChatGroq
from langchain_core.tools import tool

@tool
def customer_lookup(query: str) -> str:
    """Look up customer information."""
    return f"Customer record found for query: {query}"
agent = create_agent(
    model=model,
    tools=[customer_lookup],
    middleware=[
        PIIMiddleware(
            "email", # redact emails in the user input before sending it to the model
            strategy="redact",
            apply_to_input=True
        ),
        PIIMiddleware(
            "credit_card",
            strategy="hash",
            apply_to_input=True
        ),
        PIIMiddleware(
            "api_key",
            detector=r"gsk_[a-zA-Z0-9]{32}",
            strategy="block",
            apply_to_input=True
        ),
    ],
    )  
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "My email is testuser@company.com and my credit card is 5001-1005-0510-5100. Can you help me?"
    }]
})

print(result["messages"][-1].content) # "I found your customer record associated with [REDACTED_EMAIL]. How would you like to proceed?