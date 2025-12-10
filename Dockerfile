FROM python:3.13

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema (incluindo o Poppler)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Instalar Poetry de forma mais eficiente
ENV POETRY_HOME="/opt/poetry"
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s $POETRY_HOME/bin/poetry /usr/local/bin/poetry

# Definir ambiente Poetry e evitar criação de virtualenvs
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN poetry config virtualenvs.create false

# Copiar apenas arquivos essenciais para instalação de dependências
COPY pyproject.toml poetry.lock /app/

# Instalar dependências do projeto sem instalar o próprio projeto
RUN poetry install --no-root --no-interaction --no-ansi

# Garantir que a pasta /app não tenha restrições de permissão
RUN chmod -R 777 /app

# Copiar código-fonte da aplicação sem alterar permissões
COPY . /app

# Expor porta para execução
EXPOSE 9999

# Comando para iniciar a aplicação
CMD ["poetry", "run", "streamlit", "run", "consulta_zipdin/app.py", "--server.port=9999", "--server.address=0.0.0.0"]
