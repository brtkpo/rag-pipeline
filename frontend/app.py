import streamlit as st
import api

st.set_page_config(page_title="Local RAG Chat", layout="wide")
st.title("Local RAG Chat")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Document Upload")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file and st.button("Process PDF"):
        with st.spinner("Processing document..."):
            try:
                result = api.upload_file(uploaded_file)
                st.success(result["message"])
            except Exception as e:
                st.error(f"Upload failed: {e}")
                
    st.divider()
    st.header("Database Files")
    
    try:
        saved_files = api.get_files()
        if not saved_files:
            st.info("No documents in database.")
        else:
            for f in saved_files:
                col1, col2 = st.columns([4, 1])
                col1.write(f"📄 {f}")
                if col2.button("❌", key=f"del_{f}"):
                    api.delete_file(f)
                    st.rerun()
    except Exception:
        st.warning("Backend is unreachable.")

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