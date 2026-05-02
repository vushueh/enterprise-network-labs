#!/bin/sh
# ============================================================
# DEVICE: ATTACKER1 | PROJECT: 06 — Security Hardening
# PHASE: 1 — Port Security Test Commands
# PLATFORM: CML 2.9 — Net-Tools
# LAST UPDATED: 2026-05-02
# ============================================================
# Run manually on ATTACKER1. This is not a boot script.
# The goal is to generate multiple source MAC addresses on
# HQ-ASW2 Ethernet1/1 so port security counters can be verified.
# ============================================================

ip link show eth0

# Get a normal DHCP lease with the default MAC address.
udhcpc -i eth0

# Generate a second source MAC address. This should still be allowed
# because HQ-ASW2 E1/1 is configured for maximum 2 secure MACs.
ip link set eth0 down
ip link set eth0 address 02:06:06:06:00:01
ip link set eth0 up
udhcpc -i eth0

# Generate a third source MAC address. This should trigger the
# port-security violation counter in restrict mode.
ip link set eth0 down
ip link set eth0 address 02:06:06:06:00:02
ip link set eth0 up
udhcpc -i eth0

# If udhcpc is unavailable, generate any traffic after each MAC change,
# then verify on HQ-ASW2 with:
# show port-security interface Ethernet1/1
# show port-security address interface Ethernet1/1
# show logging | include PSECURE
