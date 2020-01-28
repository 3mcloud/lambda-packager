FROM amazonlinux:2018.03

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


RUN wget https://www.python.org/ftp/python/3.7.6/Python-3.7.6.tgz

RUN tar xzf Python-3.7.6.tgz
RUN cd Python-3.7.6 && autoreconf -i && ./configure --enable-optimizations && make altinstall
RUN rm Python-3.7.6.tgz

RUN python3.7 -m pip install --upgrade pip

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD /entrypoint.sh

