ARG BASE_IMAGE=python:3.12-slim-buster
FROM ${BASE_IMAGE}

# system update & package installation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    openssl libssl-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

copy . .
workdir .

#pip
RUN python3 -m pip install --user --upgrade pip && \
    python3 -m pip install --user -r requirements.txt

# configuration
EXPOSE 8000

# Execute
CMD ["sh", "-c", "alembic upgrade head && python main.py"]
