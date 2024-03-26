FROM amazonlinux:latest

ENV RUNTIME=node
ENV VERSION=20.11.*

# Install node and zip
RUN curl -sL https://rpm.nodesource.com/setup_20.x | bash -
RUN yum -y update && yum -y install nodejs-${VERSION} zip bzip2-devel

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD ["/entrypoint.sh"]
