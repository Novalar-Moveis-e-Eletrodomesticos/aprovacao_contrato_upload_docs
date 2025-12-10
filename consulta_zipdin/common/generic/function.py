import time
import os
import pypdf
import base64
import io
import streamlit as st
from pdf2image import convert_from_path

def save_token(token, expires_in, file_token):
    expires_at = time.time() + expires_in - 10
    with open(file_token, "w") as file:
        file.write(f"{token}\n{expires_at}")

def load_token(file_token):
    if not os.path.exists(file_token):
        return None

    with open(file_token, "r") as file:
        lines = file.readlines()
        if len(lines) < 2:
            return None
        
        token = lines[0].strip()
        expires_at = float(lines[1].strip())

        return token if time.time() < expires_at else None

def request_with_retries(request_func,retries=3,*args, **kwargs):
    for attempt in range(1, retries + 1):
        try:
            return request_func(*args, **kwargs)
        except Exception as e:
            if attempt < retries:
                time.sleep(2 ** attempt)
            else:
                raise

def transformar(base64_string, nome_arquivo):
    pdf_bytes = base64.b64decode(base64_string)
    pdf_stream = io.BytesIO(pdf_bytes)
    leitura = pypdf.PdfReader(pdf_stream)
    escrever = pypdf.PdfWriter()
    escrever.append_pages_from_reader(leitura)
    output_stream = io.BytesIO()
    escrever.write(output_stream)
    pdf_saida = output_stream.getvalue()
    with open(nome_arquivo, 'wb') as f:
        f.write(pdf_saida)
    return pdf_saida

def exibir_pdf_como_imagens(pdf_path):
    try:
        pages = convert_from_path(pdf_path)
        return pages
    
    except Exception as e:
        st.error(f"Erro ao processar o PDF: {e}")