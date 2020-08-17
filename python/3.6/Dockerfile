FROM amazonlinux:2017.03

RUN yum -y install git \
    python36 \
    python36-pip \
    python36-devel \
    zip \
    gcc \
    which \
    && yum clean all

RUN python3 -m pip install --upgrade pip

ENV VERSION=3.6

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY entrypoint.py /entrypoint.py
RUN chmod +x /entrypoint.py

CMD ["/usr/bin", "-c", "/entrypoint.sh"]
