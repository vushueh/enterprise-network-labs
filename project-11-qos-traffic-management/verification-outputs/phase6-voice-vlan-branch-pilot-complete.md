# Project 11 Phase 6 - Voice VLAN Branch Pilot Complete

## Result

Phase 6 completed on the branch access switch pilot.

No changes were required on `BR-RTR1` or `BR-DSW1` because precheck confirmed:

- VLAN 500 exists as `VOICE`
- Branch trunks allow and forward VLAN 500
- `BR-RTR1 Ethernet0/0.500` is up/up with gateway `10.2.50.1`

## BR-ASW1 Configuration Applied

```ios
interface Ethernet1/0
 description ACCESS-PC-BR1-VLAN100-VOICE500
 switchport access vlan 100
 switchport mode access
 switchport nonegotiate
 switchport voice vlan 500
 spanning-tree portfast
 spanning-tree bpduguard enable
!
interface Ethernet1/1
 description ACCESS-PC-BR2-VLAN200-VOICE500
 switchport access vlan 200
 switchport mode access
 switchport nonegotiate
 switchport voice vlan 500
 spanning-tree portfast
 spanning-tree bpduguard enable
```

## Verification Evidence

`show interfaces Ethernet1/0 switchport`:

```text
Access Mode VLAN: 100 (ENGINEERING)
Voice VLAN: 500 (VOICE)
```

`show running-config interface Ethernet1/1` confirmed `switchport voice vlan 500`.

`show vlan brief | include 500`:

```text
500  VOICE  active  Et1/0, Et1/1
```

## Save

```text
write memory
Building configuration...
[OK]
```

## Notes

Data VLAN behavior is unchanged. `Ethernet1/0` remains data VLAN 100 and `Ethernet1/1` remains data VLAN 200. Voice VLAN 500 is now available for tagged voice traffic from an IP phone or voice-capable endpoint.
