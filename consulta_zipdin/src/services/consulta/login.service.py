import requests
import streamlit as st
from http import HTTPStatus

class AuthService:
    def __init__(self):
        self.url_base = st.secrets['api']
        self.headers = {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        self.client_id = 'string'
        self.client_secret = 'string'

    def login(self, user, password):
        """Realiza o login do usuário utilizando as credenciais fornecidas."""
        if not user or not password:
            st.error("Usuário e senha são obrigatórios.")
            return None

        body = {
            'grant_type': 'password',
            'username': user,
            'password': password,
            'scope': '',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }

        try:
            response = requests.post(f'{self.url_base}/auth/login', data=body, headers=self.headers)
            if response.status_code == HTTPStatus.OK:
                return response.json()
            elif response.status_code == HTTPStatus.UNAUTHORIZED:
                st.error("Usuário ou senha incorretos.")
            else:
                st.error(f"Erro ao tentar realizar login. Código de status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"Erro de conexão: {e}")
            return None
