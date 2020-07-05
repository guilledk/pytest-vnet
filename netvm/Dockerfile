FROM ubuntu:18.04

USER root
WORKDIR /root

# Entrypoint contains openvswitch init & teardown, like a context manager for mininet
COPY ENTRYPOINT.sh /
RUN chmod +x /ENTRYPOINT.sh

# Garantee no prompts in dpkg
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update

# Install requirements
RUN apt-get install -y --no-install-recommends \
    git \
    wget \
    curl \
    llvm \
    tk-dev \
    xz-utils \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libffi-dev \
    liblzma-dev \
    python-openssl \
    libsqlite3-dev \
    ca-certificates \
    build-essential \
    libreadline-dev \
    libncurses5-dev \
    libncursesw5-dev

# Install mininet & openvswitch runtime
RUN apt-get install -y --no-install-recommends \
    mininet \
    tcpdump \
    iproute2 \
    net-tools \
    iputils-ping \
    openvswitch-switch \
    openvswitch-testcontroller

# Install pyenv
RUN curl https://pyenv.run | bash
ENV PATH "/root/.pyenv/bin:$PATH"
RUN echo 'eval "$(pyenv init -)"' >> .bashrc
RUN echo 'eval "$(pyenv virtualenv-init -)"' >> .bashrc

EXPOSE 6633 6653 6640

ENTRYPOINT ["/ENTRYPOINT.sh"]