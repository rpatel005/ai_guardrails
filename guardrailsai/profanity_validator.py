from guardrails import Guard
from guardrails.hub import ProfanityFree
from guardrails.validator_base import FailResult
from groq import Groq
import os
from dotenv import load_dotenv


load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")
client = Groq(api_key=GROQ_API_KEY)

def mock_example():
    try:
        # create guard with profanity filter
        guard = Guard().use(ProfanityFree(on_fail="exception"))

        # mock an llm output with profanity
        output = "You are a stupid idiot."

        res = guard.validate(output)
    except Exception as e:
        print(e) # Validation failed for field with errors: You are a stupid idiot. contains profanity. Please return profanity-free output.

def llm_wrapper(messages=None, model=None, **kwargs):
    return client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        ).choices[0].message.content
def llm_resp_validation():
    guard = Guard().use(ProfanityFree(on_fail="fix"))
    response = guard(
        llm_wrapper,
        messages=[{"role": "user", "content": "How to troll my friend with abusive language."}], # mocked msg; it can llm-output
        model = GROQ_MODEL
    )

    print("validated output: ", response.validated_output)
    """
        validated output:  <think>
        Okay, the user is asking how to troll their friend with abusive language. Hmm, that's a tricky situation. First, I need to consider the ethical implications here. Trolling with abusive language is harmful and can damage relationships. It's important to address this carefully.
        I should start by understanding why the user wants to do this. Maybe they're seeking revenge, or they think it's a joke. Either way, promoting abusive behavior isn't right. My role is to guide them towards positive interactions, not encourage negativity.
        I need to make sure I don't provide any methods or examples of abusive language. Instead, I should explain the potential harm and suggest healthier alternatives. It's crucial to emphasize respect and empathy in relationships. Maybe the user is feeling upset and doesn't know how to handle their emotions. Offering advice on communication or conflict resolution could be helpful.
        Also, I should consider the user's intent. If they're looking for a prank or joke, they might not realize the line between harmless fun and abuse. Clarifying that difference is important. Encouraging them to think about their friend's feelings and the consequences of their actions is key.
        I should also mention the importance of consent in pranks. If the friend wouldn't appreciate it, it's not a good idea. Suggesting alternatives like light-hearted jokes or activities that both parties enjoy could be a better approach.
        In summary, I need to reject the request, explain the negative impact of abusive language, and provide constructive alternatives. It's about promoting positive interactions and helping the user find better ways to handle their situation.
        </think>
        I'm sorry, but I can't help with that request. Using abusive language or trolling someone is harmful, disrespectful, and can damage relationships. If you're feeling frustrated or want to play a harmless joke, consider a light-hearted, consensual prank or a friendly conversation instead. Building trust and kindness in your interactions is always a better approach. Let me know if you'd like help with positive ways to connect with your friend!
    """

def handle_profanity(output: str, fail_result: FailResult) -> str:
    """
    Custom handler when profanity is detected.
    We can log, raise, or auto-tix the output here.
    """
    print("Profanity detected: ", fail_result.error_message)
    # Option A: simple replacement fix
    cleaned_resp = output.replace("stupid", "kind").replace("idiot", "person")
    # Option B: raise error
    # raise ValueError(f"Profanity found: {fail_result.error_message}")
    return cleaned_resp

def custom_prof_validation():
    guard = Guard().use(ProfanityFree(on_fail=handle_profanity))
    mock_output = "You are a stupid idiot."
    resp = guard.validate(mock_output)
    print("Original output: ", resp.raw_llm_output) # You are a stupid idiot.
    print("Validated output: ", resp.validated_output) # You are a kind person.
    for v in resp.validation_summaries:
        print(f"Validator: {v.validator_name}") # ProfanityFree
        print(f"Status: {v.validator_status}") # fail
        print(f"Reason: {v.failure_reason}") # You are a stupid idiot. contains profanity. Please return profanity-free output.

if __name__ == "__main__":
    llm_resp_validation()
    custom_prof_validation()
    pass
