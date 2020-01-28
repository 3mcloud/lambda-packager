FROM amazonlinux:2.0.20191217.0

RUN yum -y groupinstall "Development Tools"
RUN yum -y install git \
    wget \
    automake \
    bzip2-devel \
    libffi-devel \
    libressl-dev \
    openssl-devel \
    postgresql-dev \
    && yum clean all


RUN wget https://www.python.org/ftp/python/3.8.1/Python-3.8.1.tgz

RUN tar xzf Python-3.8.1.tgz
RUN cd Python-3.8.1 && autoreconf -i && ./configure --enable-optimizations && make altinstall
RUN rm Python-3.8.1.tgz

RUN python3.8 -m pip install --upgrade pip

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD /entrypoint.sh

