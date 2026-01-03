FROM python:3.14

ENV PIP_NO_CACHE_DIR=1
ENV SETUPTOOLS_SCM_PRETEND_VERSION_FOR_CHECKMATE=1.0.0



RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md ./
COPY checkmate ./checkmate
COPY bin ./bin

RUN pip install --upgrade pip && pip install .

ENV CODE_DIR=/workspace

ENTRYPOINT ["checkmate"]
CMD ["--help"]

