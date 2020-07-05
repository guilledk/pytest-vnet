FROM ubuntu:18.04

USER root
WORKDIR /root

COPY ENTRYPOINT.sh /
RUN chmod +x /ENTRYPOINT.sh

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
	git \
    curl \
	python3 \
	python3-pip \
	python3-setuptools

RUN apt-get install -y --no-install-recommends \
    mininet \
    tcpdump \
    iproute2 \
    net-tools \
    iputils-ping \
    openvswitch-switch \
    openvswitch-testcontroller

RUN pip3 install git+git://github.com/mininet/mininet.git

EXPOSE 6633 6653 6640

ENTRYPOINT ["/ENTRYPOINT.sh"]