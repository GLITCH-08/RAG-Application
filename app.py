import streamlit as st
from database import main as populate_db
from query import query_rag
from langchain.schema.document import Document


# Set the page configuration for Streamlit
st.set_page_config(page_title='Content Engine')

# Function to load and populate the database
def load_and_populate_database():
    st.header("Database Population")
    st.write("Use this section to populate the database.")
    if st.button("Populate Database"):
        populate_db()

    st.markdown("<hr style='border: 1px dashed #e0e0e0;'>", unsafe_allow_html=True)  


# Function to display the scrolling chat box
def display_chat_box():
    st.header("Chat Box")
    st.write("Enter your questions below and get responses generated from the context.")

    # Setup for holding old messages
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Display all the history in a scrollable chat box
    with st.container():
        for message in st.session_state.messages:
            st.chat_message(message['role']).markdown(message['content'])

    # Input field for user query
    user_query = st.chat_input("Your Query:", key="query_input")

    if user_query:
        # Display user prompt
        st.chat_message('user').markdown(user_query)

        # Store the user prompt in state
        st.session_state.messages.append({'role': 'user', 'content': user_query})

        # Buffering message while waiting for response
        with st.spinner('Waiting for response...'):
            # Query processing
            response_text = query_rag(user_query)

        # Show the LLM response
        st.chat_message('assistant').markdown(response_text)

        # Store the LLM response
        st.session_state.messages.append({'role': 'assistant', 'content': response_text})

# Main function to run the Streamlit app
def main():
    # Title and description
    st.markdown("<h1 style='font-size: 60px; text-align: center;'>🧠Content Engine🤖</h1>", unsafe_allow_html=True)
    # st.markdown("<hr style='border: 1px dashed #e0e0e0; '>", unsafe_allow_html=True)  
    # st.write("This system analyzes and compares multiple PDF documents, specifically identifying and highlighting their differences. The system will utilize Retrieval Augmented Generation (RAG) techniques to effectively retrieve, assess, and generate insights from the documents.")
    st.markdown("<hr style='border: 1px dashed #e0e0e0;'>", unsafe_allow_html=True)  
    
    # To load and populate the database
    # load_and_populate_database()
    
    # Display chat box
    display_chat_box()

    

if __name__ == "__main__":
    main()
