import streamlit as st
from src.services.consulta.consulta_service import ConsultaService

def sidebarFunction():
    with st.sidebar:
        if "user" not in st.session_state and not st.session_state["user"]:
            st.warning("Informações do usuário não encontradas.")
        
        st.markdown("## Informações do Usuário")
        
        nome = st.session_state["user"][0][0]['nome']
        filial = st.session_state["user"][0][0]['filiais'][0]['descricao']
        filiais = ConsultaService.filiais_dpt(st.session_state["user"][0][0]['idusuario'])
        
        if filiais:
            mapa_filiais = {f["numeronome"]: f["idfilial"] for f in filiais['retorno']}

            st.write(f"**Analista:** {nome.split(' ')[0]} {nome.split(' ')[1]}")
            st.write(f"**Filial:** {filial}")
            
            selecionadas = st.selectbox(
                'Selecione as filiais',
                options=list(mapa_filiais.keys()),
                placeholder='Todas'
            )

            return (st.session_state["user"][0][0]['idusuario'],mapa_filiais[selecionadas])

        else:
            st.write(f"**Analista:** {nome.split(' ')[0]} {nome.split(' ')[1]}")
            st.write(f"**Filial:** {filial}")
            
            return (st.session_state["user"][0][0]['idusuario'],st.session_state["user"][0][0]['filiais'][0]['codigo'])