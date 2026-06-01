# Project 12 Phase 3 - Timed Rebuild: HQ-DSW1

## Context

HQ-DSW1 is the HQ distribution switch. It connects to:
- HQ-RTR1 (uplink, trunk, all VLANs)
- HQ-DSW2 (LACP EtherChannel, Po1)
- HQ-ASW1 (access switch trunk)
- HQ-ASW2 (access switch trunk)

After erase/reload, HQ-DSW1 is at factory default: all ports in VLAN 1, no trunks, no SVI, no OSPF.

## Step 1 — Hostname And Management (T+60 to T+63)

```ios
enable
configure terminal
hostname HQ-DSW1
no ip domain-lookup
ip routing
username admin privilege 15 secret CMLlab2025!
enable secret CMLenableP@ss!
crypto key generate rsa modulus 2048
ip ssh version 2
line vty 0 4
 login local
 transport input ssh
line con 0
 login local
end
```

## Step 2 — VLANs (T+63 to T+65)

```ios
configure terminal
vlan 100
 name ENGINEERING
vlan 200
 name SALES
vlan 300
 name SERVERS
vlan 500
 name VOICE
vlan 999
 name MANAGEMENT
vlan 1000
 name NATIVE-UNTAGGED
end
```

## Step 3 — LACP EtherChannel To HQ-DSW2 (T+65 to T+68)

```ios
configure terminal
interface range Ethernet0/2-3
 description LACP-TO-HQ-DSW2-E0/2-3
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk native vlan 1000
 switchport trunk allowed vlan 100,200,300,500,999,1000
 channel-group 1 mode active
 no shutdown
!
interface Port-channel1
 description LACP-PO1-TO-HQ-DSW2
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk native vlan 1000
 switchport trunk allowed vlan 100,200,300,500,999,1000
!
end
```

## Step 4 — Trunks To Access Switches And Router (T+68 to T+72)

```ios
configure terminal
interface Ethernet0/0
 description TRUNK-TO-HQ-RTR1-E0/0
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk native vlan 1000
 switchport trunk allowed vlan 100,200,300,500,999,1000
 no shutdown
!
interface Ethernet0/1
 description TRUNK-TO-HQ-ASW1-E0/0
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk native vlan 1000
 switchport trunk allowed vlan 100,200,300,500,999,1000
 spanning-tree portfast trunk
 no shutdown
!
interface Ethernet1/0
 description TRUNK-TO-HQ-ASW2-E0/0
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk native vlan 1000
 switchport trunk allowed vlan 100,200,300,500,999,1000
 spanning-tree portfast trunk
 no shutdown
!
end
```

## Step 5 — Management SVI And Default Route (T+72 to T+74)

```ios
configure terminal
interface Vlan999
 description MANAGEMENT-SVI
 ip address 10.1.99.11 255.255.255.0
 no shutdown
!
ip default-gateway 10.1.99.1
!
end
```

## Step 6 — Spanning Tree (T+74 to T+76)

```ios
configure terminal
spanning-tree mode rapid-pvst
spanning-tree vlan 100,200,300,500,999,1000 priority 4096
!
interface range Ethernet0/1, Ethernet1/0
 spanning-tree portfast trunk
 spanning-tree bpduguard enable
!
end
```

## Step 7 — AAA (T+76 to T+78)

```ios
configure terminal
aaa new-model
!
tacacs server HQ-TACACS
 address ipv4 10.1.99.52
 key tacacs123
!
ip tacacs source-interface Vlan999
!
aaa authentication login default group tacacs+ local
aaa authentication login CONSOLE local
aaa authorization exec default group tacacs+ local
!
line vty 0 4
 login authentication default
 authorization exec default
 transport input ssh
!
line con 0
 login authentication CONSOLE
!
end
write memory
```

## Completion Target

HQ-DSW1 rebuild target: **T+78 minutes or less**

Proceed to post-recovery verification (Phase 4).
