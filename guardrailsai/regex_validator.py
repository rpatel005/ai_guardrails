from guardrails import Guard
from guardrails.hub import RegexMatch
from guardrails.validator_base import FailResult

def custom_fix(output, fail_result: FailResult):
    # Simple correction: capitalize first letter and ensure ending period
    text = output.strip()
    if not text.endswith('.'):
        text +='.'
    return text[0].upper() + text[1:]

guard = Guard().use(RegexMatch(regex="^[A-Z].*\.$", on_fail=custom_fix))
resp = guard.validate("This sentence doesnt end properly")
print(resp.validation_passed) # True
print(resp.validated_output) # This sentence doesnt end properly.