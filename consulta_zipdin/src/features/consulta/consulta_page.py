import os
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from src.features.consulta.consulta_controler import ConsultaController
from src.features.login.login_page import loginPage
from common.generic.function import (
    transformar, exibir_pdf_como_imagens
)
from common.sabium.sabium import sabium
from src.widgets.sidebar import sidebarFunction

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

def exibir_contrato(doc_cliente, contrato):
    status = doc_cliente['data']['results']['base64CCB']
    if status != '':
        st.write('Contrato do cliente')
        base64_str = doc_cliente['data']['results']['base64CCB']

        if os.path.exists(f'{contrato}.pdf'):
            imagens = exibir_pdf_como_imagens(f'{contrato}.pdf')
            if imagens:
                for i, page in enumerate(imagens):
                    st.image(page, caption=f"Página {i + 1}")
                return exibir_botao_aprovacao(contrato)
            else:
                st.error("Falha ao carregar as imagens do contrato.")
        else:
            transformar(base64_str, f'{contrato}.pdf')
            imagens = exibir_pdf_como_imagens(f'{contrato}.pdf')
            if imagens:
                for i, page in enumerate(imagens):
                    st.image(page, caption=f"Página {i + 1}")
                return exibir_botao_aprovacao(contrato)
            else:
                st.error("Falha ao carregar as imagens do contrato.")
    elif doc_cliente['data']['results']['status'] == 'CANCELADO' or doc_cliente['data']['results']['status'] == 'FORMALIZACAO_EXPIRADA':
        st.write('Contrato já expirado, o mesmo será cancelado.')
        ConsultaController.fecharPedido(v_contrato=contrato,v_status='N',v_obs='Contrato expirado')
        st.rerun()
    else:
        st.write('O cliente ainda não assinou o contrato.')

def consultaPage():
    if 'user' not in st.session_state:
        loginPage()

    st.set_page_config(page_title="Aprovação Contrato FIDC", layout="wide", page_icon="assets/images/favicon.png")
    st_autorefresh(interval=600000, key="refresh")
    validar_sessao = sabium.validar_sessao(st.session_state["user"][1]['pragma'])
    if not validar_sessao:
        del st.session_state["user"]
        sabium.logout()
        st.rerun()
    
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

    dados = ConsultaController.fetchConsulta(usuarioid=userid,filialid=codfil)
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
                'contratoexterno': 'Contrato'
            }, inplace=True)

            df_retorno['Pedido'] = df_retorno['Pedido'].astype(str)
            colunas = ['Filial', 'Documento Cliente', 'Nome Cliente', 'Pedido', 'Contrato']
            df = st.dataframe(
                df_retorno[colunas],
                on_select='rerun',
                selection_mode=['single-row'],
                width='stretch',
                hide_index=True
            )

            selected = df.selection.rows

            if selected:
                contratos = list(df_retorno[colunas].iloc[selected]['Contrato'].values)
                contrato = contratos[0] if contratos else None

                if contrato:
                    doc_cliente = ConsultaController.fetchZipdin(contratoexterno=f'{contrato}')
                    if doc_cliente:
                        resultado = exibir_contrato(doc_cliente,contrato)
                        if resultado:
                            if resultado[0] is True:
                                ConsultaController.fecharPedido(v_contrato=resultado[2],v_status='S',v_obs=resultado[1])
                                st.rerun()
                            elif resultado[0] is False:
                                ConsultaController.fecharPedido(v_contrato=resultado[2],v_status='N',v_obs=resultado[1])
                                st.rerun()
                            else:
                                st.error('Poderia validar somente em aprovado ou não')
                    else:
                        st.write('Contrato não encontrado ou inválido')
                        ConsultaController.fecharPedido(v_contrato=contrato,v_status='N',v_obs='Contrato não encontrado ou inválido')
                        st.rerun()
                else:
                    st.write('Contrato não encontrado ou inválido')    
    else:
        st.write('Sem nenhum contrato para validação')

consultaPage()
