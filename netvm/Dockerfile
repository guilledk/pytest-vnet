FROM debian:stretch-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install packages
RUN apt-get update && \
    apt-get install \
        --no-install-recommends \
        --no-install-suggests \
        -y \
        apt-utils ca-certificates cgroup-bin cgroup-tools cpp cpp-6 curl fontconfig-config fonts-dejavu-core git git-man iperf iproute2 iputils-ping kmod libapt-inst2.0 libatomic1 libbsd0 libcap2 libcgroup1 libcurl3 libcurl3-gnutls libelf1 liberror-perl libexpat1 libffi6 libfontconfig1 libfreetype6 libgdbm3 libgmp10 libgnutls30 libgpm2 libgssapi-krb5-2 libhogweed4 libice6 libidn11 libidn2-0 libisl15 libk5crypto3 libkeyutils1 libkmod2 libkrb5-3 libkrb5support0 libldap-2.4-2 libldap-common libmnl0 libmpc3 libmpfr4 libncurses5 libnettle6 libnghttp2-14 libp11-kit0 libpcap0.8 libperl5.24 libpng16-16 libprocps6 libpsl5 libpython-stdlib libpython2.7-minimal libpython2.7-stdlib libreadline7 librtmp1 libsasl2-2 libsasl2-modules-db libsm6 libsqlite3-0 libssh2-1 libssl1.0.2 libssl1.1 libtasn1-6 libunistring0 libutempter0 libwrap0 libx11-6 libx11-data libxau6 libxaw7 libxcb1 libxcursor1 libxdmcp6 libxext6 libxfixes3 libxft2 libxi6 libxinerama1 libxmu6 libxmuu1 libxpm4 libxrandr2 libxrender1 libxt6 libxxf86vm1 mime-support net-tools netbase openssl openvswitch-common openvswitch-switch patch perl perl-modules-5.24 procps python python-minimal python-pkg-resources python-six python2.7 python2.7-minimal readline-common socat sudo tcpdump telnet ucf uuid-runtime autotools-dev binutils file gcc-6 libasan3 libc-dev-bin libc6-dev libcc1-0 libcilkrts5 libgcc-6-dev libgomp1 libitm1 liblsan0 libltdl-dev libltdl7 libmagic-mgc libmagic1 libmpx2 libquadmath0 libsigsegv2 libtsan0 libubsan0 linux-libc-dev m4 manpages manpages-dev

# Prepare Mininet Install
RUN rm -rf /home/openflow/ && \
    mkdir /usr/share/man/man1

# Install Mininet from git
RUN git clone https://github.com/mininet/mininet.git /home/mininet/
WORKDIR /home/mininet/
RUN git checkout 2.3.0d6
# For following sed command thanks to Ozzy Johnson and his mininet dockerfile
RUN sed -e 's/\(apt-get -y install\)/\1 --no-install-recommends --no-install-suggests/g' \
    	-i /home/mininet/util/install.sh 
RUN /home/mininet/util/install.sh -fnv

# Prepare Start
EXPOSE 6633 6653 6640

COPY entrypoint.sh /home/entrypoint.sh
RUN chmod +x /home/entrypoint.sh

ENTRYPOINT [ "/home/entrypoint.sh" ]