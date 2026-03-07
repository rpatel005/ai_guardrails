from guardrails import Guard
from guardrails.hub import DetectPII
from guardrails.validator_base import FailResult
from pydantic import BaseModel
from groq import Groq
import os
from dotenv import load_dotenv

# load_dotenv()
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# GROQ_MODEL = os.getenv("GROQ_MODEL")
# client = Groq(api_key=GROQ_API_KEY)

guard = Guard().use(DetectPII(pii_entities=["EMAIL_ADDRESS", "PHONE_NUMBER"], on_fail="noop"))
resp = guard.validate("Please send details to my email address.")
print(resp.validation_passed) # True
print(resp.validated_output)  # Please send details to my email address.
if resp.validation_passed:
    print("Prompt doesnt contain any PII.")
else:
    print("Prompt contains PII data")

resp = guard.validate("Please send these details to my email address test@company.com")
print(resp.validation_passed) # False
print(resp.validated_output) # Please send these details to my email address test@company.com
if resp.validation_passed:
    print("Prompt doesnt contain any PII.")
else:
    print("Prompt contains PII data")


guard = Guard().use(DetectPII(pii_entities=["EMAIL_ADDRESS", "PHONE_NUMBER"], on_fail="fix"))
resp = guard.validate("Please contact me at testuser@company.com")
print(resp.validated_output) # Please contact me at <EMAIL_ADDRESS>

guard = Guard().use(DetectPII(pii_entities=["EMAIL_ADDRESS", "PHONE_NUMBER"], on_fail="reask")) # on_fail="reject", "fix", "reask", "noop"
resp = guard.validate("Please contact me at testuser@company.com")
print(resp.validated_output)


def custom_handler(output, error):
    print("Detected violation: ", error) 
    """Detected violation:  outcome='fail' error_message='The following text in your response contains PII:\nContact me at testuser@gmail.com' fix_value='Contact me at <EMAIL_ADDRESS>' error_spans=[] metadata=None validated_chunk=None"""
    return output.replace("gmail.com", "[redacted-email]")

guard = Guard().use(DetectPII(on_fail=custom_handler))
resp = guard.validate("Contact me at testuser@gmail.com")
print(resp.validated_output) # Contact me at testuser@[redacted-email]

guard = Guard().use(DetectPII(pii_entities=["EMAIL_ADDRESS"], on_fail=custom_handler))
resp = guard.validate("Contact me at testuser@gmail.com")
print(resp.validated_output) # Contact me at testuser@[redacted-email]


