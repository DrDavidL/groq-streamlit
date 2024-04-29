import streamlit as st
import os
from groq import Groq
import random
from prompts import *

from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.write("*Please contact David Liebovitz, MD if you need an updated password for access.*")
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True


def main():
    """
    This function is the main entry point of the application. It sets up the Groq client, the Streamlit interface, and handles the chat interaction.
    """
    
    # The title and greeting message of the Streamlit application
    st.title("Chat with Groq!")
    st.write("Hello! I'm your friendly Groq chatbot. I can help answer your questions, provide information, or just chat. I'm also super fast! Let's start our conversation!")


    if check_password():
        # Get Groq API key
        
        persona = st.sidebar.radio("Pick the persona", ("Regular user", "Physician"), index=1)
        if persona == "Regular user":
            system = system_prompt2
        else:
            system = system_prompt
        # Display the Groq logo
        spacer, col = st.columns([5, 1])  
        with col:  
            st.image('groqcloud_darkmode.png')

        # Add customization options to the sidebar
        st.sidebar.title('Customization')
        model = st.sidebar.selectbox(
            'Choose a model',
            ['llama3-8b-8192', 'mixtral-8x7b-32768', 'gemma-7b-it']
        )
        conversational_memory_length = st.sidebar.slider('Conversational memory length:', 1, 10, value = 5)

        memory=ConversationBufferWindowMemory(k=conversational_memory_length)

        # user_question = st.text_input("Ask a question:")
        chat = ChatGroq(
            groq_api_key = st.secrets['GROQ_API_KEY'], 
            model_name=model
            )

        # session state variable
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history=[]
        else:
            for message in st.session_state.chat_history:
                memory.save_context({'input':message['human']},{'output':message['AI']})


        # Initialize Groq Langchain chat object and conversation


        
        human = "{text}"
        prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])


        
        
        
        # conversation = ConversationChain(
        #         llm=groq_chat,
        #         memory=memory
        # )

        # If the user has asked a question,
        if user_question := st.chat_input("Ask a question!"):
            with st.chat_message("user"):
                st.markdown(user_question)
            chain = prompt | chat
            response = chain.invoke({"text": f'prior conversation: {st.session_state.chat_history}\n\n New input: {user_question}'})
            
            message = {'human':user_question,'AI':response.content}
            
            st.session_state.chat_history.append(message)
            with st.chat_message("assistant"):
                st.write("Chatbot:", response.content)
    if st.button("Clear chat history"):
        st.session_state.chat_history = []

if __name__ == "__main__":
    main()
    
    
    
        # if prompt := st.chat_input("Ask followup!"):
        #     st.session_state.messages.append({"role": "user", "content": prompt})
        #     with st.chat_message("user"):
        #         st.markdown(prompt)

        #     with st.chat_message("assistant"):
        #         stream = client.chat.completions.create(
        #             model=model3,
        #             messages=[
        #                 {"role": m["role"], "content": m["content"]}
        #                 for m in st.session_state.messages
        #             ],
        #             stream=True,
        #         )
        #         response = st.write_stream(stream)
        #         html = markdown2.markdown(response, extras=["tables"])
        #         st.download_button('Download Followup Response', html, f'followup_response.html', 'text/html')
        #     st.session_state.messages.append({"role": "assistant", "content": response})