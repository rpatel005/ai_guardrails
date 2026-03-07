from guardrails import Guard
from guardrails.hub import ToxicLanguage
from guardrails.validator_base import FailResult
from pydantic import BaseModel
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")
client = Groq(api_key=GROQ_API_KEY)

guard = Guard().use(ToxicLanguage, threshold=0.5, validation_method="sentence", on_fail="exception")

try: 
    guard.validate("Please look carefully. You are a stupid idiot who can't do things right.")
except Exception as e:
    print(e)
    """
    Validation failed for field with errors: The following sentences in your response were found to be toxic:
    - You are a stupid idiot who can't do things right.
    """
