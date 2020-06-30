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
    postgresql-dev \
    which \
    && yum clean all \
    && wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz \
    && tar xzf Python-${PYTHON_VERSION}.tgz \
    && cd Python-${PYTHON_VERSION} && autoreconf -i && ./configure --enable-optimizations && make altinstall \
    && cd .. \
    && rm Python-${PYTHON_VERSION}.tgz \
    && ${PYTHON3_ALIAS} -m pip install --upgrade pip

RUN echo 'alias python3="${PYTHON3_ALIAS}"' >> ~/.bashrc

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD /entrypoint.sh
