import os
from groq import Groq
import streamlit as st

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
GROQ_MODEL   = "llama-3.3-70b-versatile"
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

client = Groq(api_key=GROQ_API_KEY)

def generate_paper(topic, papers_context):
    print("\n Generating research paper draft...")
    prompt = f"""
You are an expert academic researcher. Based on the following related research papers, 
write a complete research paper on the topic: "{topic}"

Related Papers:
{papers_context}

Write the paper with these sections:
1. Title
2. Abstract (150-200 words)
3. Introduction
4. Literature Review (reference the papers above)
5. Proposed Methodology
6. Expected Results / Discussion
7. Conclusion
8. References

Use formal academic language. Be thorough and specific.
"""
    
    response = client.chat.completions.create(
        model=GROQ_MODEL, 
        messages=[
            {"role": "system", "content": "You are an expert academic researcher who writes detailed research papers."},
            {"role": "user",   "content": prompt}
        ],
        max_tokens=4000,
        temperature=0.7
    )
    return response.choices[0].message.content
