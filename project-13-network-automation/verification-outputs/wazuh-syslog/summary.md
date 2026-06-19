# Wazuh Syslog Onboarding Summary

## Goal

Send CML IOS node syslog to the Wazuh server at `192.168.10.156` so the lab
devices appear in the Wazuh Cisco/network-engineering views.

This is separate from the CML controller dashboard. The controller dashboard
shows CML lab lifecycle events. These node syslogs show what the routers and
switches themselves are doing.

## Wazuh Receiver Change

Wazuh already listened on UDP 514, but it did not allow the CML lab source
ranges. I added these source ranges to the second `<remote>` syslog block in
`/var/ossec/etc/ossec.conf`:

```xml
<allowed-ips>10.0.0.0/16</allowed-ips>
<allowed-ips>10.1.0.0/16</allowed-ips>
<allowed-ips>10.2.0.0/16</allowed-ips>
```

Before editing, I created a backup on Wazuh:

```text
/var/ossec/etc/ossec.conf.bak-cml-syslog-<timestamp>
```

Then I restarted Wazuh and confirmed the receiver:

```text
0.0.0.0:514 users:(("wazuh-remoted",pid=547420,fd=4))
```

## IOS Syslog Change

The generated apply evidence is here:

- [apply-summary.md](apply-summary.md)

Applied to 8 reachable IOS devices:

| Device | Source Interface | Wazuh Target |
|--------|------------------|--------------|
| HQ-RTR1 | Loopback0 | 192.168.10.156 |
| BR-RTR1 | Loopback0 | 192.168.10.156 |
| HQ-DSW1 | Vlan999 | 192.168.10.156 |
| HQ-DSW2 | Vlan999 | 192.168.10.156 |
| HQ-ASW1 | Vlan999 | 192.168.10.156 |
| HQ-ASW2 | Vlan999 | 192.168.10.156 |
| BR-DSW1 | Vlan999 | 192.168.10.156 |
| BR-ASW1 | Vlan999 | 192.168.10.156 |

The applied IOS baseline was:

```ios
service timestamps log datetime msec localtime show-timezone
logging origin-id hostname
logging facility local6
logging trap informational
logging source-interface <Loopback0-or-Vlan999>
logging host 192.168.10.156
```

The existing lab syslog server `10.1.99.51` was kept in place.

## Routing Fix

After the syslog config was applied, Wazuh still did not see IOS packets because
the lab routing table had no route to `192.168.10.156`.

I added only narrow host routes, not a new default route:

```ios
! HQ-RTR1
ip route 192.168.10.156 255.255.255.255 10.1.99.254

! BR-RTR1
ip route 192.168.10.156 255.255.255.255 10.0.0.1
```

Reason: this sends only Wazuh telemetry toward the CML edge and preserves the
existing project routing/NAT/firewall behavior.

## Verification

Source pings to Wazuh passed after the route fix:

| Device | Source | Result |
|--------|--------|--------|
| HQ-RTR1 | Loopback0 / 10.0.255.1 | 3/3 success |
| BR-RTR1 | Loopback0 / 10.0.255.2 | 3/3 success |
| HQ-DSW2 | Vlan999 / 10.1.99.12 | 3/3 success |
| BR-ASW1 | Vlan999 / 10.2.99.3 | 3/3 success |

Packet capture on Wazuh proved IOS syslog arrival:

```text
10.1.99.12 > 192.168.10.156.514 SYSLOG local6 notice
%SEC_LOGIN-5-LOGIN_SUCCESS: Login Success [user: admin] [Source: 10.1.99.54]
```

Wazuh indexed the Cisco IOS event:

```text
timestamp: 2026-06-19T06:51:33.769+0000
rule.id: 4722
rule.description: Cisco IOS: Successful login to the router
rule.groups: syslog, cisco_ios, authentication_success
location: 10.1.99.12
```

## Where To See It In Wazuh

Use the Cisco/network dashboard, not the CML controller dashboard:

```text
rule.groups:cisco_ios AND location:10.*
```

Useful focused searches:

```text
location:10.1.99.12
rule.groups:authentication_success AND location:10.*
data.cisco.mnemonic:LOGIN_SUCCESS
```

The CML dashboard remains for controller/lab lifecycle logs such as node boot,
node stop, and lab state heartbeats.

## 2026-06-19 Update

`WAN-RTR1` and `CML-EDGE1` are now fixed and proven in Wazuh. See:

- [2026-06-19-wan-cml-edge-update.md](2026-06-19-wan-cml-edge-update.md)

Current direct IOS syslog coverage is 10 of 10 in-scope CML IOS devices.

## Remaining Gaps

- `HQ-FW1` is still excluded because ASA SSH is refused and ASA syslog syntax is
  a separate platform workflow.
- `ISP-RTR1` is intentionally outside this monitoring scope because it
  represents the simulated ISP side. Add it later only through a deliberate
  out-of-band management or firewall/NAT design.
- Linux/service nodes should be onboarded next with rsyslog or Wazuh agents:
  `AUTOMATION1`, `HQ-TACACS`, `HQ-RADIUS`, `HQ-DHCP-DNS`, and `HQ-SYSLOG`.
