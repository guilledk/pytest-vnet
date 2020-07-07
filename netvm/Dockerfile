FROM debian:buster-slim

# Guarantee no prompts in dpkg
ENV DEBIAN_FRONTEND=noninteractive

# Update apt list
RUN apt-get update

RUN apt-get install \
	-y \
	--no-install-recommends \
	git \
	sudo \
	patch \
	net-tools \
	apt-utils \
	iputils-ping \
	ca-certificates

# Prepare Mininet Install
RUN rm -rf /home/openflow/ && \
    mkdir /usr/share/man/man1

# Install Mininet from git
RUN git clone https://github.com/mininet/mininet.git /home/mininet/
WORKDIR /home/mininet/
RUN git checkout 2.3.0d6
RUN /home/mininet/util/install.sh -fnv

# Prepare Start
EXPOSE 6633 6653 6640

COPY entrypoint.sh /home/entrypoint.sh
RUN chmod +x /home/entrypoint.sh

ENTRYPOINT [ "/home/entrypoint.sh" ]