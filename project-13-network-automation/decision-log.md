# Project 13 Decision Log

## D-01 — Use Netmiko Before Ansible

I am using Netmiko first because it teaches the Python control flow directly:
inventory parsing, connection handling, command execution, error handling, and
report generation. Ansible will be added later as a comparison, not a
replacement.

## D-02 — Keep Credentials Out Of Inventory

The inventory identifies devices only. Passwords are supplied by environment
variables such as `NETLAB_USERNAME`, `NETLAB_PASSWORD`, and `NETLAB_SECRET`.
This keeps the repo safe and makes the automation reusable.

## D-03 — Fix AUTOMATION1 Routes Before Netmiko

AUTOMATION1 had working reachability but received ICMP redirects for internal
lab routes. I fixed the routing model first:

- internal CML summaries via `10.1.99.1`
- default route via `10.1.99.254`

That makes the automation path deterministic and removes redirect noise from
testing.

## D-04 — Read-Only First

Configuration push is not allowed until the read-only collection and inventory
validation are proven. This prevents automation from becoming a faster way to
make a broad mistake.

## D-05 — Treat ASA As A Separate Platform Exception

`HQ-FW1` is reachable by ICMP, but TCP/22 is currently refused from
`AUTOMATION1`. The IOS fleet is ready for Netmiko, while the ASAv needs a
separate SSH/AAA verification pass. I am documenting it instead of hiding the
failure because ASA syntax and management behavior are materially different
from IOS/IOL.

## D-06 — Safe Marker Before Broad Standards Push

The Project 13 reference asks for a configuration push across the fleet. I am
using an unused ACL marker as the first live push candidate because it proves
automation can enter config mode, apply a known object, verify it, save it, and
roll it back without changing packet forwarding, routing, AAA, firewall policy,
or management access.

## D-07 — Ansible As Comparison

Ansible is included as an alternative workflow, but not as the main
implementation. Netmiko shows the Python/DevNet skill directly. Ansible shows
how the same operational pattern can become declarative later.
