import streamlit as st
import requests
from common.zipdin.api_zipdin import get_protected_data
from common.sabium.sabium import Sabium

class ConsultaService:
    def fetch_consulta(v_idusuario,v_idfilial):
        url = f"{Sabium().validar_rest()}/v3/executar_filtro"
        headers = {
            "accept": "application/json",
            "pragma": st.session_state["user"][1]['pragma'],
            "content-type": "application/json"
        }
        data = {
            "idfiltro": 90087,
            "idcontexto": 2,
            "parametros": [
                {"parametro": "idfilial", "valorparametro": v_idfilial},
                {"parametro": "idusuario", "valorparametro": v_idusuario}
            ]
        }

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    
    def baixar_venda(contrato,status,obs):
        url = f"{Sabium().validar_rest()}/v3/executar_filtro"
        headers = {
            "accept": "application/json",
            "pragma": st.session_state["user"][1]['pragma'],
            "content-type": "application/json"
        }
        data = {
            "idfiltro": 90088,
            "idcontexto": 2,
            "parametros": [
                {"parametro": "idusuario","valorparametro": st.session_state["user"][0][0]["idusuario"]},
                {"parametro": "contratoexterno","valorparametro": contrato},
                {"parametro": "aprovado","valorparametro": status},
                {"parametro": "obsaprovacao","valorparametro": obs}
            ]
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    
    def filiais_dpt(usuarioid):
        url = f"{Sabium().validar_rest()}/v3/executar_filtro"
        headers = {
            "accept": "application/json",
            "pragma": st.session_state["user"][1]['pragma'],
            "content-type": "application/json"
        }
        data = {
            "idfiltro": 90094,
            "idcontexto": 2,
            "parametros": [
                {"parametro": "usuario","valorparametro": usuarioid}
            ]
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    
    def zipdin(contrato):
        informacoes = get_protected_data(
            url=st.secrets['CONSULTA_URL'],
            pedido=contrato,
            tentativas=st.secrets['MAX_RETRIES'],
            filetoken=st.secrets['TOKEN_FILE_ELETRO'] if (st.session_state.empresa == '1') else  st.secrets['TOKEN_FILE_SA']
        )
        return informacoes