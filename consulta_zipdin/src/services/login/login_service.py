import streamlit as st
from common.sabium.sabium import sabium

def loginService(usuario, senha):
    try:
        pragma = sabium.login(usuario, senha)
        
        if pragma != 'Sem pragma' and pragma is not None:
            st.session_state.logged_in = True
            st.session_state.usuario = usuario
            st.success("Login bem-sucedido!")
            data = sabium.complementos(pragma=pragma)

            codigo = data[0]['filiais'][0]['codigo']
            st.session_state.empresa = str(codigo)[0]
            return data,{'pragma':pragma}
        else:
            st.session_state.logged_in = False
            return None

    except Exception as e:
        st.session_state.logged_in = False
        return None
