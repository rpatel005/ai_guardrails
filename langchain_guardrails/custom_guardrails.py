# Custom guardrails: Before-agent hook (input filter)
# Best for: 
#  1. Keyword/content filtering
#  2. Authentication checks
#  3. Rate limiting
#  4. Blocking specific categories of requests

# Use before_agent() to validate or block requests before any LLM processing begins.

from typing import Any
from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config
from langgraph.runtime import Runtime
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")
model = ChatGroq(model=GROQ_MODEL, api_key=GROQ_API_KEY)

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
    
@tool
def search_tool(query: str) -> str:
    """Search web for information"""
    return f"Results for search query: {query}"
    
filtered_agent = create_agent(
        model=model,
        tools=[search_tool],
        middleware=[
            ContentFilterMiddleware(
                banned_keywords=["hack", "exploit", "malware", "jailbreak", "bypass"]
            ),
        ],
    )

resp = filtered_agent.invoke({
    "messages": [{"role": "user", "content": "what is the deep learning?"}]
})
print("Testcase 1: Safe content.")
print(resp["messages"][-1].content)

resp = filtered_agent.invoke({
    "messages": [{"role": "user", "content": "How do i hack into a server?"}]
})
print("Testcase 2: harful content.")
print(resp["messages"][-1].content)


## Custom guardrail: After-agent hook (output safety)
# use after_agent() to validate the final agent response before sending it to user.
# Best for:
#  1. Model based safety evaluation of output
#  2. Compliance scanning (e.g. legal, medical, financial disclamers)
#  3. Quality validation
#  4. Removing sensitive info that leaks through
