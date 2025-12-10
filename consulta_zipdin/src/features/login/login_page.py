from streamlit import streamlit as st
from src.features.login.login_controller import loginController

def loginPage():
    
    st.set_page_config(page_title="Login", layout="centered", page_icon="assets/images/favicon.png")
    
    division = st.columns([1, 2, 1], vertical_alignment='top')
    with division[1]:
        st.image('assets/images/logo.webp')
    with st.form(key='login'):    
        
        username = st.text_input(
            'Usuário', placeholder='Usuário', label_visibility='hidden'
        )
        password = st.text_input(
            'Senha',
            placeholder='Senha',
            label_visibility='collapsed',
            type='password',
        )

        confirm = st.form_submit_button(label='Entrar')

        if confirm:
            loginController(username, password)