import streamlit as st
import requests
from common.zipdin.api_zipdin import get_protected_data
from common.sabium.sabium import Sabium
from common.generic.log import setup_logging

log = setup_logging()

class UploadWithValidationService:
    def fetch_consulta(v_idusuario,v_idfilial):
        url_base = st.secrets['PRODUCAO']
        url = f"{url_base}/v3/executar_filtro"
        headers = {
            "accept": "application/json",
            "pragma": st.session_state["user"][1]['pragma'],
            "content-type": "application/json"
        }
        data = {
            "idfiltro": 10289,
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
        log.info('entrou em def baixar_venda')
        url_base = st.secrets['PRODUCAO']
        url = f"{url_base}/v3/executar_filtro"
        headers = {
            "accept": "application/json",
            "pragma": st.session_state["user"][1]['pragma'],
            "content-type": "application/json"
        }
        data = {
            "idfiltro": 10290,
            "idcontexto": 2,
            "parametros": [
                {"parametro": "idusuario","valorparametro": st.session_state["user"][0][0]["idusuario"]},
                {"parametro": "contratoexterno","valorparametro": contrato},
                {"parametro": "aprovado","valorparametro": status},
                {"parametro": "obsaprovacao","valorparametro": obs}
            ]
        } 
        log.info('==================================================')
        log.info(f'url: {url}')
        log.info(f'headers: {headers}')
        log.info(f'data: {data}')
        log.info('==================================================')
        response = requests.post(url, headers=headers, json=data)
        log.info(response)
        if response.status_code == 200:
            log.info('response entrou no status 200')
            log.info(response.json())
            return response.json()
        else:
            return None