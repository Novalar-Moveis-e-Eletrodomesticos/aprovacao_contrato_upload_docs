import os
import io
import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from streamlit_autorefresh import st_autorefresh

from src.features.busca_contrato.busca_contrato_controler import BuscaContratoController
from src.features.login.login_page import loginPage
from common.generic.function import transformar
from common.sabium.sabium import sabium
from src.widgets.sidebar import sidebarFunction


def proteger_pdf(input_path: str, senha: str, output_path: str):
    """Criptografa o PDF com senha."""
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(senha)
    with open(output_path, "wb") as f:
        writer.write(f)


def busca_contrato():
    # ⚙️ Config inicial
    st.set_page_config(
        page_title="Aprovação Contrato FIDC",
        layout="wide",
        page_icon="assets/images/favicon.png"
    )

    # 🔐 Login
    if 'user' not in st.session_state:
        loginPage()
        st.stop()

    # ♻️ Auto-refresh 10min
    st_autorefresh(interval=600_000, key="refresh")

    # ✅ Validação de sessão
    user_data = st.session_state["user"][1]
    if not sabium.validar_sessao(user_data.get("pragma")):
        st.warning("Sessão expirada. Faça login novamente.")
        sabium.logout()
        del st.session_state["user"]
        st.rerun()

    # 🧭 Sidebar
    userid, codfil = sidebarFunction()

    # 🧾 Input
    st.title("📑 Download de Contrato FIDC")
    pedido = st.text_input("Número do Pedido", placeholder="Ex: 12345")

    if not pedido:
        st.info("Informe o número do pedido para iniciar a busca.")
        st.stop()

    # 🔍 Busca contrato
    try:
        with st.spinner("Buscando contrato..."):
            contrato_data = BuscaContratoController.fetchBuscaContrato(
                pedido=int(pedido),
                filialid=int(codfil)
            )
    except Exception as e:
        st.error(f"Erro ao buscar contrato: {e}")
        st.stop()

    if not contrato_data or not contrato_data.get("retorno"):
        st.warning("Pedido não encontrado ou sem contrato associado.")
        st.stop()

    informacoes = contrato_data["retorno"][0]
    contrato_str = informacoes.get("contratozd", "")
    cpf_cnpj = informacoes.get("cnpj_cpf", "")

    if not contrato_str:
        st.warning("Nenhum contrato PDF associado a este pedido.")
        st.stop()

    # 🔐 Gera senha (4 primeiros dígitos do CPF/CNPJ)
    senha = cpf_cnpj[:4] if cpf_cnpj else "0000"

    # 📦 Cria e protege o PDF
    pdf_path = f"{codfil}_{pedido}.pdf"
    pdf_protegido_path = f"{codfil}_{pedido}_protegido.pdf"

    try:
        # Gera o PDF base
        transformar(contrato_str, pdf_path)
        # Aplica proteção
        proteger_pdf(pdf_path, senha, pdf_protegido_path)

        with open(pdf_protegido_path, "rb") as file:
            st.success(f"Contrato pronto para download.")
            st.download_button(
                label="⬇️ Baixar Contrato Protegido",
                data=file,
                file_name=f"Contrato_{codfil}_{pedido}.pdf",
                mime="application/pdf",
                width='stretch',
            )
    except Exception as e:
        st.error(f"Erro ao gerar contrato protegido: {e}")
    finally:
        # 🧹 Limpeza de arquivos temporários
        for f in [pdf_path, pdf_protegido_path]:
            if os.path.exists(f):
                os.remove(f)


if __name__ == "__main__":
    busca_contrato()