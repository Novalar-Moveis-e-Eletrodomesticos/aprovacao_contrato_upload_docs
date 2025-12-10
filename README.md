# Projeto consulta ZIPDIN
### Projeto localhost
- Configurar o `secrets.toml` que deve ficar dentro da pasta `.streamlit`, temos um arquivo `secrets_example.toml` onde é uma cola do que deve colocar na arquivo secrets.
- Usar poetry para o projeto
    - Instalar pipx para instalar poetry
    ```sh
    pip install pipx
    ```
    - Instalar poetry
    ```sh
    pipx install poetry
    ```
    - Startar Projeto criando o ambiente virtual
    ```sh
    poetry install
    ```
    - Ativando ambiente virtual
    ```sh
    eval $(poetry env activate)
    ```
- Para executar o projeto
```sh
streamlit run consulta_zipdin/app.py
```
### Projeto Docker
- Bildar
```sh
docker build -t consulta_zipdin .
```
- Rodar o container
```sh
docker run -d -p 9999:9999 --name consulta_zipdin consulta_zipdin
```