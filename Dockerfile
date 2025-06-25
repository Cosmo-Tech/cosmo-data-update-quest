# syntax=docker/dockerfile:1.7-labs
FROM python:3.11-bookworm

WORKDIR /home/cduq

COPY ./cosmotech/ ./cosmotech/
ADD requirements.txt .
ADD pyproject.toml .

WORKDIR /home

RUN python3 -m pip install ./cduq

COPY ./docker-scripts/ ./scripts/

# Added default env var for CSM_PARAMETERS_ABSOLUTE_PATH to avoid errors with CoAL
ENV CSM_PARAMETERS_ABSOLUTE_PATH=/mnt/params

ENTRYPOINT ["csm-orc", "run", "/home/scripts/run.json"]