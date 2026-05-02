# HQ-SRV1 | Project 05 — Internet + NAT
# Role: Internal web server — static NAT target
# Connected: HQ-DSW1 Ethernet1/1 (VLAN 400, 10.1.40.0/24)

hostname HQ-SRV1
ip address add 10.1.40.10/24 dev eth0
ip link set dev eth0 up
ip route add default via 10.1.40.1

# keep the next line to indicate that the machine is ready
echo "READY" >/dev/console
exit 0
