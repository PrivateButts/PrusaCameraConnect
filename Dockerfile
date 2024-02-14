ARG build_mode='prod'


FROM python:3.11-slim AS base-build

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# copy pdm lock files
COPY ./pyproject.toml ./pyproject.toml
COPY ./pdm.lock ./pdm.lock

# install pdm
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir pdm


FROM base-build AS dev-build
# Freeze requirements
RUN pdm export -f requirements --dev > requirements.txt

FROM base-build AS prod-build
# Freeze requirements
RUN pdm export -f requirements > requirements.txt


FROM ${build_mode}-build AS build-venv

# Create Virtualenv and Install
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# run stage
FROM python:3.11-slim AS server

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# install dependencies
RUN apt update && apt install ffmpeg libsm6 libxext6  -y

# retrieve packages from build stage
COPY --from=build-venv /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# copy project files
COPY src/prusacameraconnect /app/

CMD ["python", "/app/main.py"]
