# Project 11 Phase 6 - Voice VLAN Branch Pilot

## Goal

Configure Voice VLAN 500 on the branch access switch path.

Pilot site: `BR-RTR1`, `BR-DSW1`, `BR-ASW1`

## Why Branch First

`BR-RTR1` already has the Voice VLAN gateway:

```ios
interface Ethernet0/0.500
 ip address 10.2.50.1 255.255.255.0
```

HQ-RTR1 Ethernet0/0.500 was previously removed — HQ voice VLAN is a future step.

## Phase 6A - Precheck

```ios
! BR-RTR1
show ip interface brief | include Ethernet0/0.500
show running-config interface Ethernet0/0.500

! BR-DSW1
show vlan brief | include 500
show interfaces trunk

! BR-ASW1
show vlan brief | include 500
show interfaces trunk
show running-config interface Ethernet1/0
show running-config interface Ethernet1/1
```

Precheck confirmed no router or distribution switch changes required:
- VLAN 500 (VOICE) exists on both switches
- Branch trunks already allow VLAN 500
- `BR-RTR1 Ethernet0/0.500` is up/up

## Phase 6B - Configure Voice VLAN On BR-ASW1

```ios
configure terminal
interface Ethernet1/0
 description ACCESS-PC-BR1-VLAN100-VOICE500
 switchport voice vlan 500
exit
interface Ethernet1/1
 description ACCESS-PC-BR2-VLAN200-VOICE500
 switchport voice vlan 500
end
write memory
```

## Verification

```ios
show vlan brief | include 500
show interfaces Ethernet1/0 switchport
show interfaces Ethernet1/1 switchport
show running-config interface Ethernet1/0
show running-config interface Ethernet1/1
```

Expected:

```text
Voice VLAN: 500 (VOICE)
Access Mode VLAN: 100 (ENGINEERING) on Ethernet1/0
Access Mode VLAN: 200 (SALES) on Ethernet1/1
500  VOICE  active  Et1/0, Et1/1
```

## Rollback

```ios
configure terminal
interface Ethernet1/0
 no switchport voice vlan
 description ACCESS-PC-BR1-VLAN100
interface Ethernet1/1
 no switchport voice vlan
 description ACCESS-PC-BR2-VLAN200
end
```
