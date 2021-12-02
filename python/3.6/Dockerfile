FROM amazonlinux:2017.03

ENV VERSION=3.6

RUN yum -y install git \
    gcc \
    python36 \
    python36-devel \
    python36-pip \
    which \
    zip \
    && yum clean all \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/bin/poetry

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install requirement-walker==0.0.9 PyYAML jsonschema

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY entrypoint.py /entrypoint.py
RUN chmod +x /entrypoint.py

CMD ["/entrypoint.sh"]
