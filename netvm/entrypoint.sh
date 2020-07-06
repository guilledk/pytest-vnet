#!/bin/sh 

echo "$(date) Entering Entrypoint"

echo "-- Starting OVS"
service openvswitch-switch start #This command may cause errors that do not interferre with at least 'mn --test pingall'
ovs-vsctl set-manager ptcp:6640

bash

echo "-- Stopping OVS"
service openvswitch-switch stop
echo "$(date) Leaving Entrypoint" 