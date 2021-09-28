FROM amazonlinux:latest

# Install node and zip
RUN curl -sL https://rpm.nodesource.com/setup_14.x | bash -
RUN yum -y update && yum -y install nodejs zip bzip2-devel


ENV RUNTIME=node
ENV VERSION=14.18

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD ["/entrypoint.sh"]
