FROM amazonlinux:2

ENV PYTHON_VERSION 3.8.1
ENV PYTHON3_ALIAS python3.8

RUN yum -y groupinstall "Development Tools" \
    && yum -y install git \
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
    && ${PYTHON3_ALIAS} -m pip install --upgrade pip

RUN ln -s $(which ${PYTHON3_ALIAS}) /usr/bin/python3

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY entrypoint.py /entrypoint.py
RUN chmod +x /entrypoint.py

CMD ["/bin/sh", "-c", "\"/entrypoint.sh\""]