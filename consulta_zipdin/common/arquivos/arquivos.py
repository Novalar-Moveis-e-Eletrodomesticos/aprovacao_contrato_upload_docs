import os

def ler_arquivo(file):
    raiz = os.getcwd()
    path = os.path.join(raiz, file)

    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        print(f"[ERRO] Arquivo '{file}' não encontrado em {path}")
        return None