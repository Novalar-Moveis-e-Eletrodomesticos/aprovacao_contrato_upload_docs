import os
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from common.generic.function import request_with_retries, save_token
from src.features.upload_with_validations.upload_with_validations_controller import UploadWithValidationsController
from src.features.login.login_page import loginPage
from common.sabium.sabium import sabium
from src.widgets.sidebar import sidebarFunction
import filetype



import datetime
from http import HTTPStatus
import json
import requests
import urllib
#from common.zipdin.api_zipdin import get_access_token

if 'should_rerun' not in st.session_state:
    st.session_state.should_rerun = False


def default_converter(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Tipo não serializável: {type(obj)}")

def get_access_token(idclient, secretclient, urltoken, mytoken,tentativas,force_new=False):
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



# Função para obter o token de autenticação
def obter_token():
    return get_access_token(
        idclient=st.secrets['CLIENT_ID_ELETRO'] if (st.session_state.empresa == '1')  else st.secrets['CLIENT_ID_SA'],
        secretclient=st.secrets['CLIENT_SECRET_ELETRO'] if (st.session_state.empresa == '1')  else st.secrets['CLIENT_SECRET_SA'],
        urltoken=st.secrets['TOKEN_URL'],
        mytoken=st.secrets['TOKEN_FILE_ELETRO'] if (st.session_state.empresa == '1') else  st.secrets['TOKEN_FILE_SA'],
        tentativas=st.secrets['MAX_RETRIES'],
        force_new=True
    )

def alterar_status(idproposta):
    sabium_url = st.secrets['API_SABIUM']
    user_sabium = st.secrets['USERSABIUM']
    password_sabium = st.secrets['PASSWORDSABIUM'] 

    valor_str = str(idproposta)

    idfilial = valor_str[:5]
    idpedidovenda = valor_str[5:]


    idfilial = int(idfilial)
    idpedidovenda = int(idpedidovenda)
    dados = {
        "idfiltro": 10279,
        "idcontexto": 2,
        "parametros": [
            {
            "parametro": "anexo",
            "valorparametro": 2,
            },
            {
            "parametro": "idfilial",
            "valorparametro": idfilial
            },
            {
            "parametro": "idpedidovenda",
            "valorparametro": idpedidovenda
            }
        ]
    }


    json_data = json.dumps(dados, indent=4, default=default_converter,ensure_ascii=False)

    username = urllib.parse.quote(user_sabium)
    password = urllib.parse.quote(password_sabium, safe='')
    login_sabium = requests.get(f'{sabium_url}/login/{username}/{password}')

    if (login_sabium.status_code == HTTPStatus.OK or 
        login_sabium.status_code == HTTPStatus.NO_CONTENT):
        pragma = login_sabium.headers['pragma']
        executar_filtro = requests.post(f'{sabium_url}/executar_filtro', headers={'pragma': f'{pragma}'}, data=json_data)

        if (executar_filtro.status_code == HTTPStatus.OK or 
            executar_filtro.status_code == HTTPStatus.NO_CONTENT):
            
            return True
    




def enviar_imagem(cpf_cnpj, id_proposta, file_image, docType, token):
    try:
        # Verificar o tipo do arquivo
        kind = filetype.guess(file_image)
        if kind is None:
            raise ValueError("Tipo de arquivo não identificado.")
        # Se for uma imagem
        if kind.mime.startswith('image'):
            image_bytes = file_image.read()
            files = {
                'file': (f"{file_image.name}", image_bytes, kind.mime)  
            }
            data = {
                'name': f"{file_image.name}",
                'type': docType,
                'idProposal': id_proposta,
                'cpfCnpj': cpf_cnpj,
            }
            url = 'https://api-zipcred.zipdin.com.br/zipcred/services/formalizationCdc/uploadWithValidations'
            headers = {
                "Authorization": f"Bearer {token}",
            }
            response = requests.post(url, headers=headers, data=data, files=files)
            return response
        
        # Se for um PDF
        elif kind.mime == 'application/pdf':
            # Processo específico para PDF (aqui você deve definir como quer enviar o PDF)
            pdf_bytes = file_image.read()
            files = {
                'file': (f"{file_image.name}", pdf_bytes, 'application/pdf')
            }
            data = {
                'name': f"{file_image.name}",
                'type': docType,
                'idProposal': id_proposta,
                'cpfCnpj': cpf_cnpj,
            }

            url = 'https://api-zipcred.zipdin.com.br/zipcred/services/formalizationCdc/uploadWithValidations'  # URL hipotética para PDF
            headers = {
                "Authorization": f"Bearer {token}",
            }
            response = requests.post(url, headers=headers, data=data, files=files)
            return response
        
        else:
            raise ValueError("Arquivo não suportado. Apenas imagens e PDFs são permitidos.")
    
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar a imagem: {e}")
        return None
    except ValueError as ve:
        print(ve)
        return None


# Função para enviar as imagens e verificar o status
def processar_imagens(cpf_cnpj, id_proposta, imagens, token):
    resultados = {}
    for docType, imagem in imagens.items():
        if imagem:
            st.write(f'Enviando imagem: {docType}...')
            response = enviar_imagem(cpf_cnpj, id_proposta, imagem, docType, token)

            if response and response.status_code == 200:
                st.success(f'Imagem {docType} enviada com sucesso!')
                resultados[docType] = response.json()  # Armazenando a resposta em formato JSON
            else:
                try:
                    # Tenta converter o texto da resposta para um dicionário JSON
                    error_json = response.json() if response.status_code != 200 else {}
                except ValueError:
                    # Se não for possível converter para JSON, considera a resposta como texto
                    error_json = {}

                # Se houver algum erro, trata a mensagem de erro
                if error_json:
                    if 'error' in error_json and 'message' in error_json['error']:
                        if error_json['error']['message'] == 'Limite de documentos excedido':
                            st.error(f'Arquivo {docType} já enviado.')
                        else:
                            st.error(f'Erro ao enviar {docType}. Mensagem: {error_json["error"]["message"]}')
                    else:
                        st.error(f'Erro ao enviar {docType}. Status: {response.text}')
                else:
                    st.error(f'Erro ao enviar {docType}. Status: {response.text}')

        else:
            st.warning(f'Imagem {docType} não foi fornecida.')
    
    return resultados

def exibirArquivo(file, mensagem):
   
    if file is not None:
        kind = filetype.guess(file)
        if kind.mime.startswith('image'):
            st.image(file, caption=mensagem, width=300)
        elif kind.mime == 'application/pdf':
            st.pdf(file, height=300, key=f'{file.name}-{datetime.datetime.now()}')




def portalAprovacao(doc_value, contrato_value):
    # Dados do usuário
    cpf_cnpj = st.text_input('CPF ou CNPJ:', value=doc_value, disabled=True)
    id_proposta = st.text_input('ID da proposta:', value=contrato_value, disabled=True)

    # Upload de arquivos
    st.subheader('Faça o upload das imagens:')
    frente = st.file_uploader('Carregar a foto do RG - Frente', type=['jpg', 'jpeg', 'png', 'pdf'])
    exibirArquivo(frente, 'Imagem do RG - Frente')
    st.divider()

    verso = st.file_uploader('Carregar a foto do RG - Verso', type=['jpg', 'jpeg', 'png', 'pdf'])
    exibirArquivo(verso, 'Imagem do RG - Verso')
    st.divider()

    self_image = st.file_uploader('Carregar a foto de Selfie', type=['jpg', 'jpeg', 'png', 'pdf'])
    exibirArquivo(self_image, 'Selfie')

    st.divider()
    observacao = st.text_input("Digite uma observação:")

    # Submissão
    if st.button('Enviar'):
        if cpf_cnpj and id_proposta and frente and verso and self_image:
            # Obter o token de autenticação
            token = obter_token()

            # Criar um dicionário com as imagens a serem enviadas
            imagens = {
                'RG_FRENTE': frente,
                'RG_VERSO': verso,
                'SELFIE': self_image
            }

            # Processar e enviar as imagens
            resultados = processar_imagens(cpf_cnpj, id_proposta, imagens, token)

            count_success = 0
        
            for _, result in resultados.items():
                # Acessando o erro de forma segura
                error = result.get('data', {}).get('results', {}).get('error', None)

                if error:
                    if error.get('message') == 'Limite de documentos excedido':
                        count_success += 1
                else:
                    status = result.get('data', {}).get('results', {}).get('status', None)
                    
                    if status == HTTPStatus.OK:
                        count_success += 1

            if count_success == 3:
                status = alterar_status(id_proposta)
                if status is True:
                
                    UploadWithValidationsController.fecharPedido(v_contrato=contrato_value, v_status='S', v_obs=observacao)
                    st.session_state.should_rerun = True  # Marca que o rerun deve acontecer
                else:
                    st.error('Erro ao fechar pedido')
            else:
                st.error('Erro no upload de algum documento.')


    # Condição para fazer o rerun se necessário
    if getattr(st.session_state, 'should_rerun', False):
        st.session_state.should_rerun = False  # Reseta o flag
        st.rerun()






def exibir_botao_aprovacao(contrato):
    observacao = st.text_input("Digite uma observação:")
    col2 = st.columns([1, 2])
    
    with col2[1]:
        coluna = st.columns([1, 2])
        with coluna[0]:
            approve = st.button("Aprovar")
        with coluna[1]:
            reject = st.button("Rejeitar")
    
    if approve:
        os.remove(f'{contrato}.pdf')
        st.success('Contrato aprovado com sucesso')
        return (True,observacao,contrato,st.session_state["user"][0][0]["idusuario"])
    elif reject:
        os.remove(f'{contrato}.pdf')
        st.success('Contrato rejeitado')
        return (False,observacao,contrato,st.session_state["user"][0][0]["idusuario"])


def consultaPage():
    if 'user' not in st.session_state:
        loginPage()
    st.set_page_config(page_title="Aprovação Contrato FIDC", layout="wide", page_icon="assets/images/favicon.png")
    st_autorefresh(interval=600000, key="refresh")

    userid,codfil = sidebarFunction()

    with st.sidebar:
        reload = st.button("Atualizar contratos", icon=':material/refresh:')
        if reload:
            validar_sessao = sabium.validar_sessao(st.session_state["user"][1]['pragma'])
            if validar_sessao:
                st.rerun()
            else:
                del st.session_state["user"]
                sabium.logout()
                st.rerun()

        exit = st.button("Sair", icon=':material/logout:')
        if exit:
            del st.session_state["user"]
            sabium.logout()
            st.rerun()

    dados = UploadWithValidationsController.fetchConsulta(usuarioid=userid,filialid=codfil)
    if dados:
        if dados['retorno'][0]['idfilial'] == 0:
            st.write(dados['retorno'][0]['nome'])
        else:

            df_retorno = pd.DataFrame(dados['retorno'])

            df_retorno.rename(columns={
                'filial': 'Filial',
                'cnpj_cpf': 'Documento Cliente',
                'nome': 'Nome Cliente',
                'idpedidovenda': 'Pedido',
                'contratoexterno': 'Contrato',
                'anexo': 'Anexo'
            }, inplace=True)

            # Alterando os valores da coluna 'Anexo' com base nas condições
            df_retorno['Anexo'] = df_retorno['Anexo'].replace({0: 'Aguardando assinatura', 1: 'Aguardando upload de imagens'})

            df_retorno['Pedido'] = df_retorno['Pedido'].astype(str)
            colunas = ['Filial', 'Documento Cliente', 'Nome Cliente', 'Pedido', 'Contrato', 'Anexo']
            df = st.dataframe(
                df_retorno[colunas],
                on_select='rerun',
                selection_mode=['single-row'],
                width='stretch',
                hide_index=True
            )

            selected = df.selection.rows
            if selected and df_retorno[colunas].iloc[selected]['Anexo'].values[0] == 2:
                st.text('Fechando pedido')
                contrato_value = df_retorno[colunas].iloc[selected]['Contrato'].values[0]
                UploadWithValidationsController.fecharPedido(v_contrato=contrato_value,v_status='S',v_obs='')
            if selected and df_retorno[colunas].iloc[selected]['Anexo'].values[0] == 'Aguardando upload de imagens':

                doc_value = df_retorno[colunas].iloc[selected]['Documento Cliente'].values[0]
                contrato_value = df_retorno[colunas].iloc[selected]['Contrato'].values[0]

                portalAprovacao(doc_value, contrato_value)

            elif (selected and 
                  df_retorno[colunas].iloc[selected]['Anexo'].values[0] != 'Aguardando upload de imagens' and 
                  df_retorno[colunas].iloc[selected]['Anexo'].values[0] != 2):
                st.text('Documento ainda não foi assinado')

    else:
        st.write('Sem nenhum contrato para validação')

consultaPage()

