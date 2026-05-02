# EXT-WEB1 | Project 05 — Internet + NAT
# Role: Simulated external web server (internet side)
# Connected: ISP-RTR1 Ethernet0/1 (203.0.113.96/28 segment)

ip address add 203.0.113.100/28 dev eth0
ip link set dev eth0 up
ip route add default via 203.0.113.97

# keep the next line to indicate that the machine is ready
echo "READY" >/dev/console
exit 0
