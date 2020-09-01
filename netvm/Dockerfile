FROM debian:stretch-slim

# Guarantee no prompts in dpkg
ENV DEBIAN_FRONTEND=noninteractive

# Update apt list
RUN apt-get update

# Mininet Requirements
RUN apt-get install \
	-y \
	--no-install-recommends \
	git \
	patch \
	net-tools \
	apt-utils \
	iputils-ping \
	ca-certificates \
	python-setuptools

# Prepare Mininet Install
RUN rm -rf /home/openflow/ && \
    mkdir /usr/share/man/man1

# Download Mininet source from git
RUN git clone https://github.com/mininet/mininet.git /home/mininet/
WORKDIR /home/mininet/
RUN git checkout 2.3.0d6

# Remove sudo, DEBIAN_FRONTEND and add --no-install-recommends &
# suggests to all apt commands inside mininet/util/install.sh
RUN sed -e 's/sudo //g' \
    	-e 's/~\//\//g' \
		-e 's/DEBIAN_FRONTEND=noninteractive //g' \
    	-e 's/\(apt-get -y install\)/\1 --no-install-recommends --no-install-suggests/g' \
    	-i /home/mininet/util/install.sh

# Compile & Install Mininet
RUN /home/mininet/util/install.sh -fnv

# Python build requirements
RUN apt-get install \
	-y \
	--no-install-recommends \
	curl \
	libbz2-dev \
	zlib1g-dev \
	libssl-dev \
	libffi-dev \
	libgdbm-dev \
	libnss3-dev \
	libsqlite3-dev \
	build-essential \
	libncurses5-dev \
	libreadline-dev

# This is to fix an issue when building python
RUN rm /usr/bin/lsb_release

# Prepare scripts directory for as_script decorator
RUN mkdir /root/scripts

# Mininet expects this file to exist, even if its empty
RUN touch /etc/network/interfaces

# Prepare Start
EXPOSE 6633 6653 6640