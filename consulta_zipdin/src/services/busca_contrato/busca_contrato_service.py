import streamlit as st
import requests
from common.zipdin.api_zipdin import get_protected_data
from common.sabium.sabium import Sabium

class BuscaContratoService:
    def busca_contrato(v_pedido,v_idfilial):
        url = f"{Sabium().validar_rest()}/v3/executar_filtro"
        headers = {
            "accept": "application/json",
            "pragma": st.session_state["user"][1]['pragma'],
            "content-type": "application/json"
        }
        data = {
            "idfiltro": 10276,
            "idcontexto": 2,
            "parametros": [
                {"parametro": "idfilial", "valorparametro": v_idfilial},
                {"parametro": "pedido", "valorparametro": v_pedido}
            ]
        }

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            return None
