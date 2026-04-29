import os
import streamlit as st

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
GROQ_MODEL   = "llama-3.3-70b-versatile"

 
