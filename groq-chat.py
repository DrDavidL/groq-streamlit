import streamlit as st
import os
from groq import Groq
import random

from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq


def main():
    """
    This function is the main entry point of the application. It sets up the Groq client, the Streamlit interface, and handles the chat interaction.
    """

    
    # Get Groq API key
    

    # Display the Groq logo
    spacer, col = st.columns([5, 1])  
    with col:  
        st.image('groqcloud_darkmode.png')

    # The title and greeting message of the Streamlit application
    st.title("Chat with Groq!")
    st.write("Hello! I'm your friendly Groq chatbot. I can help answer your questions, provide information, or just chat. I'm also super fast! Let's start our conversation!")

    # Add customization options to the sidebar
    st.sidebar.title('Customization')
    model = st.sidebar.selectbox(
        'Choose a model',
        ['llama3-8b-8192', 'mixtral-8x7b-32768', 'gemma-7b-it']
    )
    conversational_memory_length = st.sidebar.slider('Conversational memory length:', 1, 10, value = 5)

    memory=ConversationBufferWindowMemory(k=conversational_memory_length)

    user_question = st.text_input("Ask a question:")
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


    system = "You are a helpful assistant."
    human = "{text}"
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])


    
    
    
    # conversation = ConversationChain(
    #         llm=groq_chat,
    #         memory=memory
    # )

    # If the user has asked a question,
    if user_question:
        chain = prompt | chat
        response = chain.invoke({"text": f'prior conversation: {st.session_state.chat_history}\n\n New input: {user_question}'})
        
        message = {'human':user_question,'AI':response.content}
        
        st.session_state.chat_history.append(message)
        st.write("Chatbot:", response.content)

if __name__ == "__main__":
    main()