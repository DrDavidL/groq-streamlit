import streamlit as st
import os


from groq import Groq

client = Groq(
    api_key=st.secrets["GROQ_API_KEY"],
)


user_question = st.text_input("Ask a question:")

if user_question:

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Explain the importance of fast language models",
            }
        ],
        model="mixtral-8x7b-32768",
    )

    st.markdown(chat_completion.choices[0].message.content)