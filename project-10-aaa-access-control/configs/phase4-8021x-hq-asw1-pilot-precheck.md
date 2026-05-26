# Project 10 Phase 4 - 802.1X HQ-ASW1 Pilot Pre-Check

## Goal

Pilot RADIUS-backed IEEE 802.1X port authentication on one endpoint-facing access port only.

## Pilot Scope

| Role | Device / Port | Address / Purpose |
|---|---|---|
| RADIUS server | `HQ-RADIUS` | `10.1.99.53` |
| Authenticator switch | `HQ-ASW1` | Management source `Vlan999` / `10.1.99.13` |
| Pilot access port | `HQ-ASW1 Ethernet0/2` | `ACCESS-PC-ENG1-VLAN100` |

Do not enable 802.1X on trunk, uplink, management-server, or console-access paths.

## Important Safety Note

The CML endpoint on `Ethernet0/2` is not yet confirmed as an 802.1X supplicant. For this first pilot, use open authentication so the endpoint is not permanently blocked during RADIUS/802.1X visibility testing.

Keep the `HQ-ASW1` console open during the pilot.

Open authentication allows endpoint traffic before successful authentication. It proves the switch/RADIUS configuration and session visibility, but it does **not** prove unauthorized-access blocking. Closed-mode enforcement is a later test after a real supplicant is available.

## Step 1 - Check 802.1X Command Support First

Run this first on `HQ-ASW1`:

```ios
show dot1x all
```

If this command is rejected on IOL-L2, stop and paste the error before making any Phase 4 configuration changes.

Then run:

```ios
show authentication sessions
show running-config | include ^radius|^ip radius|^aaa authentication dot1x|^dot1x
```

If `show authentication sessions` is rejected, paste the error before configuring; the IOS image may use a different authentication-manager command set.

If both required commands are rejected, run these final non-disruptive alternatives before declaring an IOL-L2 visibility limitation:

```ios
show dot1x
show dot1x interface Ethernet0/2
show dot1x interface Ethernet0/2 detail
show authentication interface Ethernet0/2
show eap registrations
show aaa sessions
```

If all are unavailable, stop the fully verified 802.1X path and check whether an `IOSvL2` / `iosvl2` node image is available in CML.

## Step 2 - Verify The Existing Pilot Port

Run on `HQ-ASW1`:

```ios
show interfaces description | include Et0/2
show running-config interface Ethernet0/2
show ip interface brief | include Vlan999
ping 10.1.99.53 source Vlan999 repeat 5
```

Expected:

- `Ethernet0/2` is the test endpoint access port, not an uplink.
- `Vlan999` is up/up with management address `10.1.99.13`.
- `HQ-RADIUS` responds to ping from `Vlan999`.

## Step 3 - Confirm HQ-RADIUS Client Definition

The RADIUS server must trust requests sourced by `HQ-ASW1` management IP `10.1.99.13`.

In the `HQ-RADIUS` `clients.conf` file, confirm or add:

```text
client HQ-ASW1 {
    ipaddr = 10.1.99.13
    secret = radius123
    require_message_authenticator = no
    nas_type = cisco
}
```

Also confirm the existing test user remains present in `users`:

```text
testuser Cleartext-Password := "testpassword"
```

If this client block and the user entry already exist, do **not** restart `HQ-RADIUS`.

Restart `HQ-RADIUS` only if a file was changed. A restart may require clearing ARP for `10.1.99.53` before reachability returns.

## Step 4 - Proposed RADIUS Reachability Test Configuration

Do not apply this section until Steps 1-3 are reviewed.

Proposed on `HQ-ASW1`:

```ios
configure terminal
radius server HQ-RADIUS
 address ipv4 10.1.99.53 auth-port 1812 acct-port 1813
 key radius123
 exit
ip radius source-interface Vlan999
aaa authentication dot1x default group radius
end
write memory
```

Then test basic RADIUS authentication before touching the switchport:

```ios
test aaa group radius testuser testpassword new-code
```

## Step 5 - Proposed 802.1X Open-Mode Pilot Configuration

Apply only after RADIUS testing succeeds and we confirm the endpoint testing plan:

```ios
configure terminal
dot1x system-auth-control
interface Ethernet0/2
 description ACCESS-PC-ENG1-VLAN100-P10-DOT1X-PILOT
 authentication host-mode single-host
 authentication open
 authentication port-control auto
 dot1x pae authenticator
end
write memory
```

Verification:

```ios
show dot1x all
show authentication sessions interface Ethernet0/2
show authentication sessions interface Ethernet0/2 details
show running-config interface Ethernet0/2
```

Expected open-mode behavior:

- The access port remains usable even if the connected endpoint does not send EAPOL.
- If the endpoint is a working 802.1X supplicant, RADIUS requests may provide evidence of the authentication exchange.
- If the endpoint does not send EAPOL, no RADIUS Access-Request should be expected merely from open-auth configuration.
- No claim is made yet that an unauthorized endpoint is blocked.

## Rollback For The Pilot Port

Use from the open `HQ-ASW1` console if the endpoint is blocked unexpectedly:

```ios
configure terminal
interface Ethernet0/2
 no authentication open
 no authentication host-mode single-host
 no authentication port-control auto
 no dot1x pae authenticator
 description ACCESS-PC-ENG1-VLAN100
end
write memory
```

## Reference

Cisco IOS XE documents RADIUS connectivity, `dot1x system-auth-control`, an access-port authenticator, and verification with authentication sessions for IEEE 802.1X port-based authentication:

- https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/sec_usr_8021x/configuration/xe-3e/sec-usr-8021x-xe-3e-book/config-ieee-802x-pba.html
- https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/sec_usr_8021x/configuration/xe-3e/sec-usr-8021x-xe-3e-book/sec-ieee-open-auth.html
