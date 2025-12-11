import streamlit as st
from src.features.login.login_page import loginPage

if 'user' not in st.session_state:
    loginPage()

else:
    st.logo(
        'assets/images/novalino.png',
        icon_image='assets/images/novalino.png',
        size='large'
    )

    pages = [
        st.Page(
            'src/features/upload_with_validations/upload_with_validations_page.py',
            title='Upload Imagens',
            icon=':material/upload:'
        ),
        # st.Page(
        #     'src/features/consulta/consulta_page.py',
        #     title='Aprova contrato',
        #     icon=':material/check_box:'),
        st.Page(
            'src/features/busca_contrato/busca_contrato_page.py',
            title='Busca contrato',
            icon=':material/assignment_returned:'
        )
        
    ]

    navigation = st.navigation({
        'Páginas': pages
    })
    navigation.run()