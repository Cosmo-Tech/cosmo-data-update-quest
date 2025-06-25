FROM python:3.11-bookworm AS base

WORKDIR /home/cduq

COPY ./cosmotech/ ./cosmotech/
ADD requirements.txt .
ADD pyproject.toml .

RUN python3 -m pip install .

# Added default env var for CSM_PARAMETERS_ABSOLUTE_PATH to avoid errors with CoAL
ENV CSM_PARAMETERS_ABSOLUTE_PATH=/mnt/params

FROM base AS added_scripts
WORKDIR /home

COPY ./docker-scripts/ ./scripts/

FROM added_scripts AS runnable
ENTRYPOINT ["csm-orc", "run", "/home/scripts/run.json"]