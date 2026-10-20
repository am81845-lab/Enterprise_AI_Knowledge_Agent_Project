from __future__ import annotations
import os
import streamlit as st
from dotenv import load_dotenv
from src.auth import login_panel, logout
from src.rag import KnowledgeBase, answer_question
from src.ingestion import save_uploaded_files, build_index, list_documents, clear_index

load_dotenv()
st.set_page_config(page_title="Enterprise AI Knowledge Agent", page_icon="🧠", layout="wide")

st.markdown("""
<style>
:root { --ink:#18212f; --muted:#667085; --accent:#6d5dfc; }
.block-container { padding-top: 1.6rem; max-width: 1250px; }
.hero { padding: 1.5rem 1.7rem; border-radius: 18px; background: linear-gradient(120deg,#171d36,#303c69); color: white; margin-bottom: 1.1rem; }
.hero h1 { margin: 0 0 .35rem 0; font-size: 2.1rem; }
.hero p { color: #e2e7ff; margin: 0; }
.small-muted { color: var(--muted); font-size: .9rem; }
[data-testid="stSidebar"] { border-right: 1px solid #e8eaf0; }
.source-card { border: 1px solid #e6e8ef; padding: .85rem 1rem; border-radius: 12px; margin: .5rem 0; }
</style>
<div class="hero"><h1>🧠 Enterprise AI Knowledge Agent</h1><p>Ask questions across your PDFs, Word documents, and text files — with grounded answers and source citations.</p></div>
""", unsafe_allow_html=True)

if "user" not in st.session_state:
    st.session_state.user = None
if not st.session_state.user:
    login_panel()
    st.stop()

user = st.session_state.user
with st.sidebar:
    st.markdown("### Workspace")
    st.write(f"Signed in as **{user['username']}**")
    st.caption(f"Role: {user['role'].title()}")
    page = st.radio("Navigate", ["AI Knowledge Chat", "Admin Dashboard"] if user['role'] == 'admin' else ["AI Knowledge Chat"], label_visibility="collapsed")
    st.divider()
    st.caption("Local document index • Gemini-powered answers")
    if st.button("Sign out", use_container_width=True):
        logout()

kb = KnowledgeBase()
if page == "Admin Dashboard":
    st.header("Admin Dashboard")
    st.write("Upload documents and rebuild the local semantic index. Supported formats: PDF, DOCX, TXT.")
    col1, col2, col3 = st.columns(3)
    docs = list_documents()
    with col1: st.metric("Stored documents", len(docs))
    with col2: st.metric("Indexed chunks", kb.chunk_count())
    with col3: st.metric("Vector index", "Ready" if kb.is_ready() else "Not built")
    uploads = st.file_uploader("Choose knowledge files", type=["pdf", "docx", "txt"], accept_multiple_files=True)
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Save uploads", type="primary", use_container_width=True, disabled=not uploads):
            try:
                saved = save_uploaded_files(uploads)
                st.success(f"Saved {len(saved)} file(s). Select Build / Rebuild Index to index them.")
                st.rerun()
            except Exception as e:
                st.error(str(e))
    with c2:
        if st.button("Build / Rebuild Index", use_container_width=True):
            with st.spinner("Extracting text, chunking, embedding and indexing documents…"):
                try:
                    count = build_index()
                    st.success(f"Index built successfully: {count} text chunks.")
                except Exception as e:
                    st.error(f"Index build failed: {e}")
    st.subheader("Knowledge files")
    if docs:
        for d in docs:
            st.write(f"📄 {d['name']} · {d['size_kb']:.1f} KB")
    else:
        st.info("No documents uploaded yet.")
    st.divider()
    st.subheader("Index maintenance")
    st.warning("Clearing the index removes indexed vectors and chunk metadata. Uploaded source files are kept.")
    if st.button("Clear vector index", type="secondary"):
        clear_index()
        st.success("Index cleared.")
        st.rerun()
else:
    st.header("AI Knowledge Chat")
    if not kb.is_ready():
        st.info("The knowledge index is empty. Ask an administrator to upload documents and build the index.")
    st.caption("Answers are based on retrieved document excerpts. If the documents do not contain the answer, the agent should say so.")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("Sources used"):
                    for i, source in enumerate(msg["sources"], 1):
                        st.markdown(f"**[{i}] {source['source']}** · chunk {source['chunk_id']}")
                        st.caption(source["text"])
    prompt = st.chat_input("Ask a question about your enterprise documents…", disabled=not kb.is_ready())
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Searching documents and preparing an answer…"):
                try:
                    result = answer_question(prompt, kb)
                    st.markdown(result["answer"])
                    if result["sources"]:
                        with st.expander("Sources used", expanded=True):
                            for i, source in enumerate(result["sources"], 1):
                                st.markdown(f"**[{i}] {source['source']}** · chunk {source['chunk_id']}")
                                st.caption(source["text"])
                    st.session_state.messages.append({"role": "assistant", "content": result["answer"], "sources": result["sources"]})
                except Exception as e:
                    st.error(f"Could not answer the question: {e}")
                    st.caption("Check your GEMINI_API_KEY in .env and ensure the vector index is built.")
    if st.session_state.messages and st.button("Clear chat history"):
        st.session_state.messages = []
        st.rerun()

st.divider()
st.caption("Prototype note: API-based generation sends retrieved excerpts to Google Gemini. Do not upload confidential data unless your organization has approved this processing arrangement.")
