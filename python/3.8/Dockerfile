FROM amazonlinux:2

ENV PYTHON_VERSION 3.8.3

ENV PYTHON_COMMAND python3.8

ENV DEFAULT_USER lambdapackager

RUN yum -y install \
        git \
        wget \
        util-linux \
        tar \
        zip \
        rsync \
        make \
        gcc-c++ \
        zlib-devel \
        bzip2-devel \
        shadow-utils \
        openssl-devel \
        postgresql-dev \
        libffi-devel && \
    wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz && \
    tar xzf Python-${PYTHON_VERSION}.tgz && \
    cd Python-${PYTHON_VERSION} && \
    ./configure --enable-optimizations && \
    make altinstall && \
    cd .. && \
    rm Python-${PYTHON_VERSION}.tgz && \
    rm -rf Python-${PYTHON_VERSION} && \
    ${PYTHON_COMMAND} -m pip install --upgrade pip

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD /entrypoint.sh
