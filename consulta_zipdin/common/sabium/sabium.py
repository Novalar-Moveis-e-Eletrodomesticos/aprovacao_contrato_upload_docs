import requests
from time import sleep
from urllib.parse import quote
import urllib.parse
import streamlit as st


class Sabium:
    
    def validar_rest(self):
        urls = []
        urls.append(st.secrets['PRODUCAO'])
        
        for url in urls:
            try:
                result = urllib.parse.urlparse(url)
                if not all([result.scheme, result.netloc]):
                    print(f"URL inválida: {url}")
                    continue

                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    return url
                else:
                    print(f"URL {url} não retornou sucesso: {response.status_code}")
            
            except requests.exceptions.RequestException as e:
                print(f"Erro ao tentar acessar {url}: {e}")
        
        print("Nenhuma URL disponível.")
        return None            
    
    def _request(self, url, headers=None, retries=4):
        for attempt in range(retries):
            try:
                response = requests.get(url, headers=headers)
                return response
            except requests.exceptions.RequestException as e:
                sleep(2 ** attempt)
        st.error(f"Falha ao se conectar com a base Sabium após {retries} tentativas.")
    
    def login(self, v_usuario, v_senha):
        encode_login = quote(v_usuario)
        encode_password = quote(v_senha)
        url = f'{self.validar_rest()}/v3/login/{encode_login}/{encode_password}'
        try:
            login_sabium = self._request(url)
            if login_sabium.status_code == 200 or login_sabium.status_code == 204:
                return login_sabium.headers.get('pragma', 'Sem pragma')
            elif login_sabium.status_code == 401:
                st.error("Credenciais incorretas")
            else:
                st.error(f"Erro inesperado: {login_sabium.status_code}")
        
        except Exception as e:
            raise
    
    def logout(self):
        url = f'{self.validar_rest()}/v3/logout'
        try:
            self._request(url)
            return True
        except Exception as e:
            raise
    
    def complementos(self, pragma):
        url = f'{self.validar_rest()}/v3/login_complementos?ambiente=funcionario'
        headers = {
            'pragma': pragma,
            'accept': 'application/json'
        }

        try:
            response = self._request(url, headers=headers)
            return response.json().get('retorno')
        except Exception as e:
            raise
    
    def validar_sessao(self, pragma):
        url = f'{self.validar_rest()}/v3/login_validar'
        headers = {
            'pragma': pragma,
            'accept': 'application/json'
        }

        try:
            response = self._request(url, headers=headers)
            if response.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            raise

sabium = Sabium()