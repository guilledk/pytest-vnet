#!/bin/sh

# while :
# do
#   sleep 1000
# done

service openvswitch-switch start
ovs-vsctl set-manager ptcp:6640

bash