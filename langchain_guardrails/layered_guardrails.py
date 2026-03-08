from typing import Any
from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config, PIIMiddleware, HumanInTheLoopMiddleware
from langgraph.runtime import Runtime
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from langchain.messages import AIMessage
from dotenv import load_dotenv
import os

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")
model = ChatGroq(model=GROQ_MODEL, api_key=GROQ_API_KEY)

@tool
def search_tool(query: str) -> str:
    """Search the web fro information."""
    return f"Search reasult for query: {query}"

@tool
def send_email_tool(to: str, subject: str, body: str) -> str:
    """Send email to a recipient."""
    return f"Email sent to {to} with subject: {subject}"

@tool
def delete_records(table: str, condition: str) -> str:
    """Delete records from the database."""
    return f"Delete records from {table} where {condition}"

class ContentFilterMiddleware(AgentMiddleware):
    """
    Deterministic guardrail: Block requests containing banned/harmful keywaors.
    This runs BEFORE the agent processes anything - zero LLM cost for blocked requests.
    """

    def __init__(self, banned_keywords: list[str]):
        super().__init__()
        self.banned_keywords = [kw.lower() for kw in banned_keywords]

    @hook_config(can_jump_to=["end"])
    def before_agent_filter(self, state: AgentState, runtime: Runtime) -> dict[str, any] | None:
        if not state["messages"]:
            return None
        first_message = state["messages"][0]
        if first_message.type != "human":
            return None
        content = first_message.content.lower()
        for kw in self.banned_keywords:
            if kw in content:
                print(f"Blocked - keyword detected: '{kw}'")
                return {
                    "messages":[{
                        "role": "assistant",
                        "content": (
                            "I cannot process requests containing harmful content."
                            "Please rephrase your request."
                            )
                    }],
                    "jump_to": "end"
                }
        return None  

class SafetyGuardrailMiddleware(AgentMiddleware):
    """Model-based guardrail: Use an LLM to evaluate response safety."""

    def __init__(self):
        super().__init__()
        self.safety_model = init_chat_model("qwen/qwen3-32b", model_provider="groq")

    @hook_config(can_jump_to=["end"])
    def after_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        # Get the final AI response
        if not state["messages"]:
            return None

        last_message = state["messages"][-1]
        if not isinstance(last_message, AIMessage):
            return None

        # Use a model to evaluate safety
        safety_prompt = f"""Evaluate if this response is safe and appropriate.
        Respond with only 'SAFE' or 'UNSAFE'.

        Response: {last_message.content}"""

        result = self.safety_model.invoke([{"role": "user", "content": safety_prompt}])

        if "UNSAFE" in result.content:
            last_message.content = "I cannot provide that response. Please rephrase your request."

        return None

prod_agent = create_agent(
    model=model,
    tools=[search_tool, send_email_tool, delete_records],
    middleware=[
        ContentFilterMiddleware(banned_keywords=["hack", "expoit", "malware"]),
        PIIMiddleware("email", strategy="redact", apply_to_input=True),
        PIIMiddleware("credit_card", strategy="mask", apply_to_input=True),
        HumanInTheLoopMiddleware(interrupt_on={"send_email_tool": True, "search_tool": False}),
        #PIIMiddleware("email", strategy="redact", apply_to_output=True),
        SafetyGuardrailMiddleware(),
    ],
    checkpointer=InMemorySaver(),
)
config = {"configurable": {"thread_id": "session_001"}}
result = prod_agent.invoke({
    "messages": [{"role": "user", "content": "How do I make explosives?"}],
},
config=config)

print("*******Agent with layered guardrails*******")
print(result["messages"][-1].content)
"""
*******Agent with layered guardrails*******
I'm sorry, but I can't provide information on making explosives. This is a dangerous and illegal activity that can cause serious harm to people and property. Explosives are heavily regulated for a reason, and creating them without proper authorization violates laws in nearly every country. If you're interested in chemistry or engineering, I encourage you to explore safe, legal fields like pyrotechnics (under professional supervision) or scientific research. Always prioritize safety and follow the law.
"""