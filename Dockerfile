FROM python:3.10-slim-buster

ENV COLUMNS 160
ENV TERM xterm-256color
ARG APP_HOME=/usr/src/app
WORKDIR ${APP_HOME}

RUN apt-get update && apt-get install --no-install-recommends -y

RUN pip install "poetry==1.1.14"

COPY ./pyproject.toml ${APP_HOME}
COPY ./poetry.lock ${APP_HOME}

RUN poetry install --no-dev

COPY . ${APP_HOME}

ENTRYPOINT ["poetry", "run", "python", "main.py"]
