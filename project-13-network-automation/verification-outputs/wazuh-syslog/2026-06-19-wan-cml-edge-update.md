# Wazuh Syslog Update - WAN-RTR1 and CML-EDGE1

Date: 2026-06-19

## Goal

Close the two remaining direct IOS syslog gaps in the CML lab:

- `WAN-RTR1` at `10.0.255.3`
- `CML-EDGE1` at `10.1.99.254`

## WAN-RTR1

Project 10 showed that `WAN-RTR1` had been touched during the AAA and local
fallback work. The Project 13 automation could reach the device, but SSH login
failed because the credential state did not match the automation baseline.

I recovered it from the CML console, preserved TACACS AAA, reset the local
fallback `admin` account, added Wazuh as a second syslog target, and saved the
configuration.

Relevant non-secret config state:

```text
aaa authentication login default group tacacs+ local
aaa authorization exec default group tacacs+ local
logging origin-id hostname
logging facility local6
logging trap informational
logging source-interface Loopback0
logging host 10.1.99.51
logging host 192.168.10.156
```

Verification:

```text
ping 192.168.10.156 source Loopback0 repeat 5
Success rate is 100 percent (5/5)
```

Wazuh indexed a fresh Cisco config-change alert:

```text
location:10.0.255.3
rule.description:Cisco IOS: Router configuration changed
data.cisco.mnemonic:CONFIG_I
```

## CML-EDGE1

`CML-EDGE1` was reachable by console and could ping Wazuh, but SSH refused
connections because local SSH access was incomplete.

I added a local admin account, generated RSA keys, enabled SSHv2, configured VTY
login, added Wazuh as a syslog target, and saved the configuration.

Relevant non-secret config state:

```text
ip domain name lab.local
ip ssh version 2
line vty 0 4
 login local
 transport input ssh
 exec-timeout 15 0
logging origin-id hostname
logging facility local6
logging trap informational
logging source-interface Ethernet0/1
logging host 192.168.10.156
```

Verification:

```text
ping 192.168.10.156 source Ethernet0/1 repeat 5
Success rate is 100 percent (5/5)

nc -vz 10.1.99.254 22
Connection to 10.1.99.254 22 port [tcp/ssh] succeeded!
```

Wazuh indexed fresh Cisco config-change alerts:

```text
location:10.1.99.254
rule.description:Cisco IOS: Router configuration changed
data.cisco.mnemonic:CONFIG_I
```

## Final Direct IOS Syslog Coverage

Final Wazuh query window: last 45 minutes.

| Source IP | Device | Direct Wazuh Alert Count |
|-----------|--------|--------------------------|
| `10.0.255.1` | `HQ-RTR1` | `1` |
| `10.0.255.2` | `BR-RTR1` | `1` |
| `10.0.255.3` | `WAN-RTR1` | `1` |
| `10.1.99.11` | `HQ-DSW1` | `1` |
| `10.1.99.12` | `HQ-DSW2` | `1` |
| `10.1.99.13` | `HQ-ASW1` | `1` |
| `10.1.99.14` | `HQ-ASW2` | `1` |
| `10.2.99.2` | `BR-DSW1` | `1` |
| `10.2.99.3` | `BR-ASW1` | `1` |
| `10.1.99.254` | `CML-EDGE1` | `2` |

Result: all 10 in-scope CML IOS devices now have direct syslog evidence in
Wazuh.

## Remaining Monitoring Expansion

- `HQ-FW1` is ASA, not IOS. It needs a separate ASA SSH/syslog procedure.
- `ISP-RTR1` is intentionally outside the current monitoring scope because it
  represents the simulated ISP side. Add it only through an explicit
  out-of-band management or firewall/NAT design.
- Linux/service nodes should use rsyslog or Wazuh agents depending on whether I
  want lightweight service logs or richer endpoint telemetry.
