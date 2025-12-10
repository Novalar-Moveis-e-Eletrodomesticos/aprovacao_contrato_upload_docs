import streamlit as st
from src.services.login.login_service import loginService

def loginController(username, password):
    response = loginService(username,password)
    if response:
        st.session_state['user'] = response
        st.rerun()