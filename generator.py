from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)

def generate_paper(topic, papers_context):
    print("\nGenerating research paper...")

    prompt = f"""
You are an expert academic researcher. Based on the following related research papers,
write a complete IEEE-style research paper on the topic: "{topic}"

Related Papers:
{papers_context}

Write the paper with EXACTLY these sections and labels:

## Abstract
(150-200 words)

## I. Introduction
(detailed introduction)

## II. Literature Review
(reference the papers above with author and year)

## III. Proposed Methodology
(detailed methodology. Include a Python code snippet inside ```python ... ``` blocks 
showing a relevant algorithm or implementation related to the topic)

## IV. Results and Discussion
(expected results and analysis)

## V. Conclusion
(summary and future work)

## VI. References
(list all referenced papers in IEEE format)

Use formal IEEE academic language. Be thorough and specific.
Include exactly ONE python code block in the Methodology section.
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": "You are an expert IEEE academic researcher."},
            {"role": "user",   "content": prompt}
        ],
        max_tokens=4000,
        temperature=0.7
    )
    return response.choices[0].message.content
