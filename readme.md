Guardrails in AI:
Safety boundaries, protective limits and control mechanism that keep a model's behaviour on the right, safe, and controlled path. E.g: guardrail-ai, nemo-guardrails, openai-guardrails etc
Ensures:
1. correctness (data types, structure)
2. Consistency (output always in expected format)
3. Control (boundaries, LLM follows)
4. Safety (no toxic, offensive, PII leakage)

Flake8 : pre-hook for autocheck coding conventions
pytest: automated test
pydantic: input-output schema validation of APIs

[openai-guardrails](https://openai.github.io/openai-guardrails-python/)

[guardrailsai](https://guardrailsai.com/guardrails/docs/how-to-guides/using_llms)

[nvidia-nemo-guardrails](https://docs.nvidia.com/nemo/guardrails/latest/index.html)

[LMQL-ai](https://lmql.ai/docs/)

[Llama-Guard](https://huggingface.co/meta-llama/Llama-Guard-3-8B)

## Microsoft Presidio: an open-source privacy toolkit 
## Presidio-analyzer: 
The Presidio analyzer is a Python based service for detecting PII entities in text. During analysis, it runs a set of different PII Recognizers, each one in charge of detecting one or more PII entities using different mechanisms. Scans text (or other data) and detects PII entities such as names, e-mails, phone numbers, credit-card numbers, Aadhaar IDs, etc. It returns the entity type, position, confidence score and optional explanation for every match. [github](https://microsoft.github.io/presidio/analyzer/?utm_source=chatgpt.com)	

## Presidio-anonymizer:
Takes the Analyzer’s findings and masks, redacts or replaces each PII span using operators like mask, replace, hash, or custom logic— and can even de-anonymize if you keep a mapping. [github](https://microsoft.github.io/presidio/anonymizer/)
The Presidio-Anonymizer package contains both Anonymizers and Deanonymizers.
Anonymizers are used to replace a PII entity text with some other value by applying a certain operator (e.g. replace, mask, redact, encrypt)
Deanonymizers are used to revert the anonymization operation. (e.g. to decrypt an encrypted text).

## Configure guardrails CLI
> In terminal: guardrails configure

> guardrails hub install hub://guardrails/profanity_free

> guardrails hub install hub://guardrails/regex_match

> guardrails hub list 
Installed Validators:
- RegexMatch
- DetectPII (redact, mask, hash, block)
- DetectJailbreak
- ProfanityFree
- ToxicLanguage

## LangChain guardrails
# Two approaches: Deterministic and Model based
1. Deterministic Guardrails
Rule-based: regex, keyword matching, explicit checks
Fast, predictable, cost-effective
May miss nuanced violations

2. Model-based Guardrails
Uses LLMs/Classifiers for semantic understanding
Catches subtle/nuanced issues
Slower and more expensive

## Human-in-the-loop middleware guardrail
Pause agent execution before sensitive operations and waits for human approval. E.g:
- Financial transaction
- Sending emails to external parties
- Deleting production data
- Any operation with significant business impact
Key requirement: A checkpointer for state persistence across interruptions.

## Custom guardrails in langchain
1. Custom guardrails: Before-agent hook (input filter)
Best for: 
- Keyword/content filtering
- Authentication checks
- Rate limiting
- Blocking specific categories of requests

 Use before_agent() to validate or block requests before any LLM processing begins.

2. After-agent hook (output safety)
   use after_agent() to validate the final agent response before sending it to user.
   Best for:
- Model based safety evaluation of output
- Compliance scanning (e.g. legal, medical, financial disclamers)
- Quality validation
- Removing sensitive info that leaks through

3. Layered Guardrails
Stack multiple guardrails in the middleware=[] array. They get executed in order, building layered protection.

User Input
    ↓
Layer 1: ContentFilteringMiddleware   <-  Deterministic input filtering
    ↓
Layer 2: PIIMiddleware (input)        <- PII redaction on input
    ↓
Layer 3: HumanInTheLoopMiddleware     <- Approval for sensitive tools
    ↓
Layer 4: PIIMiddleware (Output)       <- PII redaction of output
    ↓
Layer 5: SafetyGuardrailMiddleware    <- MOdel-based output safety
    ↓
User Response
