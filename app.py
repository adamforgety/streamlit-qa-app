import streamlit as st
from openai import OpenAI

# Initialize OpenAI client (reads OPENAI_API_KEY from environment/secrets)
client = OpenAI()

st.title("Closed-Source LLM QA App (GPT-3.5)")

user_question = st.text_input("Ask a question:")

if user_question:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_question}]
    )
    st.write("### Answer:")
    st.write(response.choices[0].message.content)