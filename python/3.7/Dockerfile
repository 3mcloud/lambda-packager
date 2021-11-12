FROM amazonlinux:2018.03

ENV PYTHON_VERSION 3.7.6
ENV PYTHON3_ALIAS python3.7

RUN yum -y groupinstall "Development Tools" && \
    yum -y install git \
    wget \
    automake \
    bzip2-devel \
    libffi-devel \
    libressl-dev \
    openssl-devel \
    sqlite-devel \
    postgresql-dev \
    which \
    && yum clean all \
    && wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz \
    && tar xzf Python-${PYTHON_VERSION}.tgz \
    && cd Python-${PYTHON_VERSION} && autoreconf -i && ./configure --enable-optimizations && make altinstall \
    && cd .. \
    && rm Python-${PYTHON_VERSION}.tgz \
    && ${PYTHON3_ALIAS} -m pip install --upgrade pip \
    && ${PYTHON3_ALIAS} -m pip install requirement-walker==0.0.9 PyYAML jsonschema \
    && curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python3

RUN ln -s $(which ${PYTHON3_ALIAS}) /usr/bin/python3

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY entrypoint.py /entrypoint.py
RUN chmod +x /entrypoint.py

CMD ["/entrypoint.sh"]
