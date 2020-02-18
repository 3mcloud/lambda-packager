FROM amazonlinux:latest

# Install C and wget
RUN yum -y update && yum -y groupinstall "Development Tools" && yum -y install \
    gcc44 \
    gcc-c++ \
    libgcc44 \
    bzip2-devel \
    cmake \
    wget \
    tar \
    gzip \
    make \
    automake

# Install node
# RUN wget http://nodejs.org/dist/v12.16.0/node-v12.16.0.tar.gz && \
#   tar -zxvf node-v12.16.0.tar.gz && \
#   cd node-v12.16.0 && ./configure && make && \
#   make install
RUN curl -sL https://rpm.nodesource.com/setup_12.x | bash -
RUN yum -y update && yum -y install nodejs



ENV VERSION=12.16.0

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD /entrypoint.sh

# CMD ["/bin/bash"]