"""
This file configures the page layout, initializes session states, 
renders the sidebar for document management (upload/delete), and 
handles the interactive chat interface for querying the LLM.
"""

import streamlit as st
import api

st.set_page_config(page_title="RAG Chat", layout="wide", initial_sidebar_state="collapsed")
st.markdown("<h1 style='text-align: center;'>RAG Chat</h1>", unsafe_allow_html=True)

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Document Upload")
    
    try:
        saved_files = api.get_files()
    except Exception:
        saved_files = []
        st.warning("Backend is unreachable.")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file", 
        type="pdf", 
        key=f"uploader_{st.session_state.uploader_key}"
    )
    
    action_placeholder = st.empty()
    
    if uploaded_file:
        if action_placeholder.button("Process PDF"):
            action_placeholder.button("Processing document...", disabled=True)
            
            try:
                result = api.upload_file(uploaded_file)

                st.toast(f"{uploaded_file.name} has been processed!", icon="✅")
                
                st.session_state.uploader_key += 1

                st.rerun()
            except Exception as e:
                error_msg = str(e)
                if "409" in error_msg:
                    st.error("Duplicate detected: A document with this exact content already exists in the database!")
                else:
                    st.error(f"Upload failed: {error_msg}")
                    
    st.divider()
    st.header("Database Files")
    
    if not saved_files:
        st.info("No documents in database.")
    else:
        with st.container(height=500):
            for f in saved_files:
                col1, col2 = st.columns([4, 1])
                col1.write(f"📄 {f}")
                if col2.button("❌", key=f"del_{f}"):
                    api.delete_file(f)
                    st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about your document..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                answer = api.ask_question(prompt)
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"Chat error: {e}") 