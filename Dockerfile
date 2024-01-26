# build stage
FROM python:3.11-slim AS builder

# install PDM
RUN pip install -U pip setuptools wheel
RUN pip install pdm

# copy files
COPY pyproject.toml pdm.lock /app/

# install dependencies and project into the local packages directory
WORKDIR /app
RUN mkdir __pypackages__ && pdm sync --prod --no-editable


# run stage
FROM python:3.11-slim

WORKDIR /app

# install dependencies
RUN apt update && apt install ffmpeg libsm6 libxext6  -y

# retrieve packages from build stage
ENV PYTHONPATH=/app/pkgs
COPY --from=builder /app/__pypackages__/3.11/lib /app/pkgs

# retrieve executables
COPY --from=builder /app/__pypackages__/3.11/bin/* /bin/

# copy project files
COPY src/prusacameraconnect /app/

CMD ["python", "/app/main.py"]
