from guardrails import Guard
from pydantic import BaseModel
from typing import List
from openai import OpenAI
from groq import Groq
import os
from dotenv import load_dotenv


load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")

class MovieReview(BaseModel):
    title: str
    sentiment: str # +ve or -ve
    descriptions: List[str]

guard = Guard.for_pydantic(output_class=MovieReview)

def schema_validation(input_schema):
        validated_output = guard.parse(input_schema)
        print("Validated output: ",validated_output) 
        """Validated output:  ValidationOutcome(
            call_id='2724580641520',
            raw_llm_output='<think>\nOkay, the user wants a JSON response for a movie review of Inception. Let me start by recalling the movie\'s details. Inception is a sci-fi action film directed by Christopher Nolan. The sentiment needs to be either positive or negative. Since the movie is generally well-received, I\'ll go with positive.\n\nNow, the descriptions should be 2-3 bullet points. I need to summarize the plot without spoilers. First point could mention the concept of entering dreams to plant ideas. Second, the complex narrative structure and visuals. Third, the performances by the cast, especially Leonardo DiCaprio. Let me check if that\'s accurate. Yeah, those elements are key to the movie. Make sure the JSON keys are correct: title, sentiment, descriptions. No markdown, just valid JSON. Alright, putting it all together.\n</think>\n\n```json\n{\n  "title": "Inception",\n  "sentiment": "positive",\n  "descriptions": [\n    "A mind-bending exploration of dreams and reality, blending intricate plot layers with stunning visuals.",\n    "Features a compelling narrative about a thief who steals secrets by infiltrating the subconscious.",\n    "Praises its cast\'s performances, particularly Leonardo DiCaprio, and the film\'s innovative action sequences."\n  ]\n}\n```',
            validation_summaries=[],
            validated_output={
                'title': 'Inception',
                'sentiment': 'positive',
                'descriptions': [
                    'A mind-bending exploration of dreams and reality, blending intricate plot layers with stunning visuals.',
                    'Features a compelling narrative about a thief who steals secrets by infiltrating the subconscious.',
                    "Praises its cast's performances, particularly Leonardo DiCaprio, and the film's innovative action sequences."
                ]
            },
            reask=None,
            validation_passed=True,
            error=None
        )"""
        if validated_output.validation_passed:
            print("Schema validation passed!")
            print(validated_output.validated_output)
        else:
            print("Schema validation failed!")
            print(f"Reason: {validated_output.reask.fail_results[0].error_message}")

def ai_generated_schema():
        client = Groq(api_key=GROQ_API_KEY)
     
        prompt = """
            Generate a structured JSON response for a movie review with the following keys:
            - title: name of the movie
            - sentiment: 'positive' or 'negative'
            - descriptions: a list of 2-3 bullet points summarizing the movie

            Movie: Inception
            """

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that always responds in valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        generated_output = response.choices[0].message.content
        return generated_output

if __name__ == "__main__":
     # mock model output
    raw_output1 = """
    {
    "title": "Inception",
    "sentiment": "positive",
    "descriptions": ["Mind-bending plot", "Brilliant direction"]
    }
    """
    schema_validation(raw_output1)
    """Validated output:  ValidationOutcome(
    call_id='1716199366864',
    raw_llm_output='\n    {\n    "title": "Inception",\n    "sentiment": "positive",\n    "descriptions": ["Mind-bending plot", "Brilliant direction"]\n    }\n    ',
    validation_summaries=[],
    validated_output={
        'title': 'Inception',
        'sentiment': 'positive',
        'descriptions': ['Mind-bending plot', 'Brilliant direction']
    },
    reask=None,
    validation_passed=True,
    error=None
    )"""


    raw_output2 = """
    {
    "title": "Inception",
    "sentiment": "positive",
    "test": ["Mind-bending plot", "Brilliant direction"]
    }
    """
    schema_validation(raw_output2)
    """Validated output:  ValidationOutcome(
    call_id='2644634313792',
    raw_llm_output='\n    {\n    "title": "Inception",\n    "sentiment": "positive",\n    "test": ["Mind-bending plot", "Brilliant direction"]\n    }\n    ',
    validation_summaries=[],
    validated_output=None,
    reask=SkeletonReAsk(
        incorrect_value={'title': 'Inception', 'sentiment': 'positive'},
        fail_results=[
            FailResult(
                outcome='fail',
                error_message='JSON does not match schema:\n{\n  "$": [\n    "\'descriptions\' is a required property"\n  ]\n}',
                fix_value=None,
                error_spans=None,
                metadata=None,
                validated_chunk=None
            )
        ],
        additional_properties={}
    ),
    validation_passed=False,
    error=None
    )"""
    
    ai_output_schema = ai_generated_schema()   
    schema_validation(ai_output_schema)
    """Validated output:  ValidationOutcome(
    call_id='2724580641520',
    raw_llm_output='<think>\nOkay, the user wants a JSON response for a movie review of Inception. Let me start by recalling the movie\'s details. Inception is a sci-fi action film directed by Christopher Nolan. The sentiment needs to be either positive or negative. Since the movie is generally well-received, I\'ll go with positive.\n\nNow, the descriptions should be 2-3 bullet points. I need to summarize the plot without spoilers. First point could mention the concept of entering dreams to plant ideas. Second, the complex narrative structure and visuals. Third, the performances by the cast, especially Leonardo DiCaprio. Let me check if that\'s accurate. Yeah, those elements are key to the movie. Make sure the JSON keys are correct: title, sentiment, descriptions. No markdown, just valid JSON. Alright, putting it all together.\n</think>\n\n```json\n{\n  "title": "Inception",\n  "sentiment": "positive",\n  "descriptions": [\n    "A mind-bending exploration of dreams and reality, blending intricate plot layers with stunning visuals.",\n    "Features a compelling narrative about a thief who steals secrets by infiltrating the subconscious.",\n    "Praises its cast\'s performances, particularly Leonardo DiCaprio, and the film\'s innovative action sequences."\n  ]\n}\n```',
    validation_summaries=[],
    validated_output={
        'title': 'Inception',
        'sentiment': 'positive',
        'descriptions': [
            'A mind-bending exploration of dreams and reality, blending intricate plot layers with stunning visuals.',
            'Features a compelling narrative about a thief who steals secrets by infiltrating the subconscious.',
            "Praises its cast's performances, particularly Leonardo DiCaprio, and the film's innovative action sequences."
        ]
    },
    reask=None,
    validation_passed=True,
    error=None
    )"""