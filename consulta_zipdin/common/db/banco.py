import streamlit as st
from sqlalchemy import create_engine, text
from time import sleep

MAX_ATTEMPTS = 4

class Banco():

    def _conexao(base):
        urls = {
            'sabium': st.secrets["SABIUM"],
            'dw':st.secrets["DW"]
        }
        
        if base not in urls:
            print("Base informada não encontrada. Favor informar equipe de desenvolvimento")
            return False
        
        for attempt in range(MAX_ATTEMPTS):
            try:
                engine = create_engine(urls[base])
                conexao = engine.connect()
                print(f"Conexão >>> OK | Base: {base}")
                return conexao
            except Exception as e:
                print(f"Conexão >>> T | Base: {base} | Tentativa: {attempt + 1} de {MAX_ATTEMPTS} | Erro: {e}")
                sleep(2 ** attempt)

        print(f"Conexão >>> OFF | Base: {base} | Após {MAX_ATTEMPTS} tentativas")
        raise ConnectionError(f"Falha na conexão com a base {base} após {MAX_ATTEMPTS} tentativas.")
    
    def _consulta(params, sql, base):
        for attempt in range(MAX_ATTEMPTS):
            try:
                session = Banco._conexao(base)
                resultado = session.execute(text(sql), params).fetchall()

                if not resultado:
                    print(f"Consulta >>> T | Nenhum resultado encontrado para o parâmetro: {params} | Base: {base}")
                    return None
                
                print(f"Consulta >>> OK | Base: {base}")
                return resultado
            except Exception as e:
                print(f"Consulta >>> T | Tentativa: {attempt + 1} de {MAX_ATTEMPTS} | Erro: {e}")
                sleep(2 ** attempt)

            finally:
                if session:
                    session.close()

    def _filiais(empresa):
        sql = 'SELECT idfilial FROM glb.filial WHERE idempresa = :empresa AND idfilial NOT IN (10002,10031,10036,10044,10046,10050,10051,20002,20015,20024,20025) ORDER BY 1'
        base = 'sabium'
        params = {'empresa':empresa}
        for attempt in range(MAX_ATTEMPTS):
            try:
                session = Banco._conexao(base)
                resultado = session.execute(text(sql), params).fetchall()

                if not resultado:
                    print(f"Consulta >>> T | Nenhum resultado encontrado para o parâmetro: {params} | Base: {base}")
                    return None
                
                print(f"Consulta >>> OK | Base: {base}")
                return resultado
            except Exception as e:
                print(f"Consulta >>> T | Tentativa: {attempt + 1} de {MAX_ATTEMPTS} | Erro: {e}")
                sleep(2 ** attempt)

            finally:
                if session:
                    session.close()