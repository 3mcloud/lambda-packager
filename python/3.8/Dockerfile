FROM python:3.8.1-alpine3.11

RUN apk add --no-cache bash \
    git \
    zip \
    gcc \
    musl-dev \
    libc-dev \
    libffi-dev \
    openssl-dev \
    libressl-dev \
    postgresql-dev


RUN python3 -m pip install --upgrade pip

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD /entrypoint.sh

