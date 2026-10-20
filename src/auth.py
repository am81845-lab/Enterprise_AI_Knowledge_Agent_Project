from __future__ import annotations
import hmac
import os
import streamlit as st


def _matches(candidate: str, configured: str) -> bool:
    return bool(configured) and hmac.compare_digest(candidate.encode("utf-8"), configured.encode("utf-8"))


def login_panel() -> None:
    st.subheader("Sign in to your knowledge workspace")
    st.write("Use the credentials configured by the project administrator in the `.env` file.")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)
    if submitted:
        admin_user = os.getenv("ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD", "")
        employee_user = os.getenv("EMPLOYEE_USERNAME", "employee")
        employee_password = os.getenv("EMPLOYEE_PASSWORD", "")
        if _matches(username, admin_user) and _matches(password, admin_password):
            st.session_state.user = {"username": username, "role": "admin"}
            st.rerun()
        elif _matches(username, employee_user) and _matches(password, employee_password):
            st.session_state.user = {"username": username, "role": "employee"}
            st.rerun()
        else:
            st.error("Invalid username or password. Check your .env configuration.")
    if not os.getenv("ADMIN_PASSWORD") or not os.getenv("EMPLOYEE_PASSWORD"):
        st.warning("Set ADMIN_PASSWORD and EMPLOYEE_PASSWORD in `.env` before using the app.")


def logout() -> None:
    st.session_state.user = None
    st.session_state.pop("messages", None)
    st.rerun()
