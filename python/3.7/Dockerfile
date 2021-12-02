FROM amazonlinux:2018.03

ENV PYTHON_BASE_VERSION 3.7
ENV PYTHON_PINNED_VERSION 3.7.12
ENV PYTHON3_ALIAS python3.7

RUN yum -y groupinstall "Development Tools" && \
    yum -y install git \
    autoconf-archive \
    automake \
    bzip2-devel \
    libffi-devel \
    libressl-dev \
    openssl-devel \
    postgresql-dev \
    sqlite-devel \
    wget \
    which \
    && yum clean all \
    && rm -rf /var/cache/yum \
    && wget https://www.python.org/ftp/python/${PYTHON_PINNED_VERSION}/Python-${PYTHON_PINNED_VERSION}.tgz \
    && tar xzf Python-${PYTHON_PINNED_VERSION}.tgz \
    && cd Python-${PYTHON_PINNED_VERSION} && autoreconf -i && ./configure --enable-optimizations && make altinstall \
    && cd .. \
    && rm Python-${PYTHON_PINNED_VERSION}.tgz \
    && ${PYTHON3_ALIAS} -m pip install --upgrade pip \
    && ${PYTHON3_ALIAS} -m pip install requirement-walker==0.0.9 PyYAML jsonschema \
    && curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python${PYTHON_BASE_VERSION} \
    && ln -s $(which ${PYTHON3_ALIAS}) /usr/bin/python3 \
    && ln -s /root/.local/bin/poetry /usr/bin/poetry

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY entrypoint.py /entrypoint.py
RUN chmod +x /entrypoint.py

CMD ["/entrypoint.sh"]
