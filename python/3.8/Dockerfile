FROM amazonlinux:2.0.20191217.0

RUN yum -y groupinstall "Development Tools" \
    && yum -y install git \
    wget \
    automake \
    bzip2-devel \
    libffi-devel \
    libressl-dev \
    openssl-devel \
    postgresql-dev \
    && yum clean all \
    && wget https://www.python.org/ftp/python/3.8.1/Python-3.8.1.tgz \
    && tar xzf Python-3.8.1.tgz \
    && cd Python-3.8.1 && autoreconf -i && ./configure --enable-optimizations && make altinstall \
    && cd .. \
    && rm Python-3.8.1.tgz \
    && python3.8 -m pip install --upgrade pip

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD /entrypoint.sh

