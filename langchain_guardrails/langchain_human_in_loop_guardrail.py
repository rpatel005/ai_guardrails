from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")

model = ChatGroq(model=GROQ_MODEL, api_key=GROQ_API_KEY)


@tool
def search_web(query: str) -> str:
    """Search the web fro information."""
    return f"Search reasult for query: {query}"

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send email to a recipient."""
    return f"Email sent to {to} with subject: {subject}"

@tool
def delete_records(table: str, condition: str) -> str:
    """Delete records from the database."""
    return f"Delete records from {table} where {condition}"

# create agent with human-in-the-loop middleware
hitl_agent = create_agent(
    model= model,
    tools=[search_web, send_email, delete_records],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "send_email": True, # require approval
                "delete_records": True, # require approval
                "search_web": False, # auto approval
            }
        ),
    ],
    checkpointer=InMemorySaver(), # !required for state persistence
)

# invoke agent will pause before send_email
config = {"configurable": {"thread_id": "session_001"}}
result = hitl_agent.invoke(
    {"messages": [{"role": "user", "content": "Send an email to testuser@company.com about the Q2 results."}]},
    config=config
)

print("*******Agent paused for human approval*******")
print(result["messages"][-1].content)

# Human review and approval
approved_result = hitl_agent.invoke(
    Command(resume={"decisions": [{"type": "approve"}]}),
    config=config # same thread_id resumes the paused session
)

print("*******Aprroved! Final response!*******")
print(approved_result["messages"][-1].content)
"""
*******Aprroved! Final response!*******
The email has been successfully sent to testuser@company.com with the subject "Q2 Results" and the body "Please find attached the Q2 results report." Let me know if you need any further assistance!
"""

# Alternatively: human rejection
config2 = {"configurable": {"thread_id": "session_002"}}
hitl_agent.invoke(
    {"messages": [{"role": "user", "content": "Delete all records from the users table where active=false"}]},
    config=config2
)

rejected_result = hitl_agent.invoke(
    Command(resume={"decisions": [{"type": "reject", "reason": "Sensitive data, DBA review required."}]}),
    config=config2
)

print("*****Rejected: Final response.*****")
print(rejected_result["messages"][-1].content)
"""
*****Rejected: Final response.*****
It looks like the deletion request was rejected. Would you like me to:

1. Confirm the records that would be deleted?
2. Adjust the condition (e.g., check for `active='false'` instead)?
3. Perform a dry-run first to see affected records?
4. Or would you like to try the deletion again?

Let me know how you'd like to proceed!
"""