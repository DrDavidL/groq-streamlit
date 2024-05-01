import streamlit as st
import markdown2
from groq import Groq
from prompts import *



# Set OpenAI API key from Streamlit secrets
groq_client = Groq(api_key = st.secrets['GROQ_API_KEY'])

st.set_page_config(
    page_title='Fast Helpful Chat',
    page_icon='🌌',
    initial_sidebar_state='expanded'
)
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
def parse_groq_stream(stream):
    for chunk in stream:
        if chunk.choices:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

st.title("Fast Helpful Chat")
st.caption('Powered by [Groq](https://groq.com/).')
st.info("Enter your questions at the bottom of the page!")

if check_password():
    
    st.sidebar.title('Customization')
    st.session_state.model = st.sidebar.selectbox(
            'Choose a model',
            ['llama3-70b-8192', 'llama3-8b-8192', 'mixtral-8x7b-32768', 'gemma-7b-it']
        )
    if st.sidebar.checkbox("Change personality? (Will clear history.)"):
        persona = st.sidebar.radio("Pick the persona", ("Regular user", "Physician"), index=1)
        if persona == "Regular user":
            system = st.sidebar.text_area("Make your own system prompt or use as is:", value=system_prompt2)
        else:
            system = system_prompt
        st.session_state.messages = [{"role": "system", "content": system}]
    else:
        st.session_state.messages = [{"role": "system", "content": system_prompt}]
    if "response" not in st.session_state:
        st.session_state["response"] = ""

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": system}]

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message(message["role"], avatar="👩‍💻"):
                st.markdown(message["content"])
        elif message["role"] == "assistant":
            with st.chat_message(message["role"], avatar="🤖"):
                st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What's up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user", avatar="👩‍💻"):
            st.markdown(prompt)
            
            # Display assistant response in chat message container
        with st.chat_message("assistant", avatar="🤖"):        
            stream = groq_client.chat.completions.create(
                model=st.session_state["model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                temperature=0.0,
                stream=True,
            )
            st.session_state.response = st.write_stream(parse_groq_stream(stream))
            
            
            
        st.session_state.messages.append({"role": "assistant", "content": st.session_state.response})

    if st.session_state["response"]:
        conversation_str = ""
        for message in st.session_state.messages:
            if message["role"] == "user":
                conversation_str += "👩‍💻: " + message["content"] + "\n\n"
            elif message["role"] == "assistant":
                conversation_str += "🤖: " + message["content"] + "\n\n"
        html = markdown2.markdown(conversation_str, extras=["tables"])
        st.download_button('Download Response', html, f'response.html', 'text/html')
    
    if st.sidebar.button("Clear chat history"):
        st.session_state.messages = []