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
	sudo \
	patch \
	net-tools \
	apt-utils \
	iputils-ping \
	ca-certificates \
	python-setuptools

# Prepare Mininet Install
RUN rm -rf /home/openflow/ && \
    mkdir /usr/share/man/man1

# Install Mininet from git
RUN git clone https://github.com/mininet/mininet.git /home/mininet/
WORKDIR /home/mininet/
RUN git checkout 2.3.0d6
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

# Prepare Start
EXPOSE 6633 6653 6640

# Sleep forever
COPY sleep.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/sleep.sh
ENTRYPOINT ["sleep.sh"]