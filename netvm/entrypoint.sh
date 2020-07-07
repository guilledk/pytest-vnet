#!/bin/sh 

service openvswitch-switch start > /dev/null
ovs-vsctl set-manager ptcp:6640 > /dev/null

bash

service openvswitch-switch stop > /dev/null