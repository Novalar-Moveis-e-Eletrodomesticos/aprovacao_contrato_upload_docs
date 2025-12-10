import requests
import os
import streamlit as st
from common.generic.function import (
    save_token,
    load_token,
    request_with_retries
)

def get_access_token(idclient, secretclient, urltoken, mytoken,tentativas,force_new=False):
    if not force_new:
        token = load_token(file_token=mytoken)
        if token:
            return token

    def request_token():
        payload = {
            "grant_type": "client_credentials",
            "client_id": idclient,
            "client_secret": secretclient
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(urltoken, data=payload, headers=headers)

        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            expires_in = data.get("expires_in", 3600)
            save_token(token, expires_in, mytoken)
            return token
        else:
            raise Exception(f"Erro ao obter token: {response.text}")

    return request_with_retries(request_func=request_token,retries=tentativas)

def get_protected_data(url, pedido, tentativas, filetoken):
    """Realiza a requisição autenticada e renova o token se necessário."""

    token = get_access_token(
        idclient= st.secrets['CLIENT_ID_ELETRO'] if (st.session_state.empresa == '1')  else st.secrets['CLIENT_ID_SA'],
        secretclient=st.secrets['CLIENT_SECRET_ELETRO']  if (st.session_state.empresa == '1')  else st.secrets['CLIENT_SECRET_SA'],
        urltoken=st.secrets['TOKEN_URL'],
        mytoken=st.secrets['TOKEN_FILE_ELETRO'] if (st.session_state.empresa == '1') else  st.secrets['TOKEN_FILE_SA'],
        tentativas=st.secrets['MAX_RETRIES']
    )

    for attempt in range(2):
        def request_data():
            payload = {"nuContratoExterno": pedido}
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            response = requests.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                if os.path.exists(filetoken):
                    os.remove(filetoken)
                raise Exception("Token expirado ou inválido.")
            elif response.status_code == 403:
                return None
            else:
                raise Exception(f"Erro na requisição: {response.status_code} - {response.text}")

        try:
            return request_with_retries(request_func=request_data,retries=tentativas)
        except Exception as e:
            if "Token expirado" in str(e) and attempt == 0:
                token = get_access_token(
                    st.secrets['CLIENT_ID_ELETRO'] if (st.session_state.empresa == '1')  else st.secrets['CLIENT_ID_SA'],
                    st.secrets['CLIENT_SECRET_ELETRO'] if (st.session_state.empresa == '1')  else st.secrets['CLIENT_SECRET_SA'],
                    st.secrets['TOKEN_URL'],
                    force_new=True
                )
                continue
            else:
                raise