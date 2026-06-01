# Project 12 Phase 2 - Timed Rebuild: HQ-RTR1

## Priority Order

HQ-RTR1 is the highest-priority rebuild target:
1. It is the OSPF ABR connecting HQ LAN to the WAN
2. It holds the GRE tunnel to BR-RTR1
3. It is the TACACS+ source-interface router for all management AAA
4. It carries the QoS WAN policy

Rebuild HQ-RTR1 first before touching HQ-DSW1 or HQ-FW1.

## Step 1 — Basic Hostname And Management (T+00 to T+05)

```ios
enable
configure terminal
hostname HQ-RTR1
no ip domain-lookup
ip domain-name lab.local
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

## Step 2 — Interface Addressing (T+05 to T+12)

```ios
configure terminal
interface Loopback0
 description ROUTER-ID-LOOPBACK
 ip address 10.0.255.1 255.255.255.255
 no shutdown
!
interface Ethernet0/0
 description HQ-TO-HQ-DSW1-E0/0
 no shutdown
!
interface Ethernet0/0.100
 description GATEWAY-VLAN100-ENGINEERING
 encapsulation dot1Q 100
 ip address 10.1.100.1 255.255.255.0
 service-policy input P11-MARK-IN
!
interface Ethernet0/0.200
 description GATEWAY-VLAN200-SALES
 encapsulation dot1Q 200
 ip address 10.1.200.1 255.255.255.0
!
interface Ethernet0/0.999
 description GATEWAY-VLAN999-MANAGEMENT
 encapsulation dot1Q 999
 ip address 10.1.99.1 255.255.255.0
!
interface Ethernet0/1
 description WAN-TO-BR-RTR1-E0/1
 ip address 10.0.0.1 255.255.255.252
 service-policy output P11-WAN-SHAPE-1M
 no shutdown
!
interface Ethernet0/2
 description WAN-TO-WAN-RTR1-E0/1
 ip address 10.0.0.5 255.255.255.252
 no shutdown
!
interface Tunnel0
 description GRE-TO-BR-RTR1-TUN0-P08
 ip address 10.0.100.1 255.255.255.252
 tunnel source Ethernet0/1
 tunnel destination 10.0.0.2
 ip mtu 1400
 ip tcp adjust-mss 1360
 ip ospf message-digest-key 1 md5 OSPF-WAN-KEY
 ip ospf cost 5
 no shutdown
!
end
```

## Step 3 — OSPF (T+12 to T+18)

```ios
configure terminal
router ospf 1
 router-id 10.0.255.1
 area 0 authentication message-digest
 passive-interface default
 no passive-interface Ethernet0/1
 no passive-interface Ethernet0/2
 no passive-interface Tunnel0
 network 10.0.0.0 0.0.0.3 area 0
 network 10.0.0.4 0.0.0.3 area 0
 network 10.0.100.0 0.0.0.3 area 0
 network 10.0.255.1 0.0.0.0 area 0
 network 10.1.99.0 0.0.0.255 area 0
 network 10.1.100.0 0.0.0.255 area 0
 network 10.1.200.0 0.0.0.255 area 0
!
interface Ethernet0/1
 ip ospf message-digest-key 1 md5 OSPF-WAN-KEY
 ip ospf cost 100
!
interface Ethernet0/2
 ip ospf message-digest-key 1 md5 OSPF-WAN-KEY
 ip ospf cost 10
!
end
```

## Step 4 — IKEv2 And IPsec GRE Encryption (T+18 to T+28)

```ios
configure terminal
crypto ikev2 proposal P08-IKEV2-PROPOSAL
 encryption aes-cbc-256
 integrity sha256
 group 14
!
crypto ikev2 policy 10
 proposal P08-IKEV2-PROPOSAL
!
crypto ikev2 keyring P08-KEYRING
 peer BR-RTR1
  address 10.0.0.2
  pre-shared-key local VPNpsk2025!
  pre-shared-key remote VPNpsk2025!
!
crypto ikev2 profile P08-IKEv2-PROFILE
 match identity remote address 10.0.0.2 255.255.255.255
 authentication local pre-share
 authentication remote pre-share
 keyring local P08-KEYRING
!
crypto ipsec transform-set P08-TRANSFORM esp-256-aes esp-sha256-hmac
 mode transport
!
crypto ipsec profile P08-IPSEC-PROFILE
 set transform-set P08-TRANSFORM
 set ikev2-profile P08-IKEv2-PROFILE
 set pfs group14
!
interface Tunnel0
 tunnel protection ipsec profile P08-IPSEC-PROFILE
!
end
```

## Step 5 — TACACS+ AAA (T+28 to T+35)

```ios
configure terminal
aaa new-model
!
tacacs server HQ-TACACS
 address ipv4 10.1.99.52
 key tacacs123
!
ip tacacs source-interface Loopback0
!
aaa authentication login default group tacacs+ local
aaa authentication login CONSOLE local
aaa authorization exec default group tacacs+ local
aaa accounting commands 15 default start-stop group tacacs+
aaa accounting exec default start-stop group tacacs+
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
```

## Step 6 — QoS Class-Maps And Policies (T+35 to T+50)

```ios
configure terminal
!
class-map match-any P11-VOICE-LIKE
 description P11 voice-like realtime traffic classification
 match protocol rtp
!
class-map match-any P11-SIGNALING
 description P11 voice signaling and control traffic classification
 match protocol sip
!
class-map match-any P11-BULK-DATA
 description P11 bulk and lower-priority application traffic
 match protocol ftp
 match protocol http
!
class-map match-any P11-NETWORK-CONTROL
 description P11 routing and infrastructure control traffic
 match protocol ospf
 match protocol dns
!
ip access-list extended P11-HTTP-TRAFFIC
 permit tcp host 10.1.100.194 host 10.1.40.10 eq www
!
class-map match-any P11-BULK-DATA-ACL
 match access-group name P11-HTTP-TRAFFIC
!
class-map match-any P11-DSCP-VOICE
 description P11 WAN queue match for DSCP EF
 match dscp ef
!
class-map match-any P11-DSCP-SIGNALING
 description P11 WAN queue match for DSCP CS3
 match dscp cs3
!
class-map match-any P11-DSCP-NETWORK-CONTROL
 description P11 WAN queue match for DSCP CS2
 match dscp cs2
!
class-map match-any P11-DSCP-BULK
 description P11 WAN queue match for DSCP AF11
 match dscp af11
!
policy-map P11-MARK-IN
 class P11-VOICE-LIKE
  set dscp ef
 class P11-SIGNALING
  set dscp cs3
 class P11-NETWORK-CONTROL
  set dscp cs2
 class P11-BULK-DATA
  set dscp af11
 class P11-BULK-DATA-ACL
  set dscp af11
!
policy-map P11-WAN-QUEUE
 class P11-DSCP-VOICE
  priority percent 30
 class P11-DSCP-SIGNALING
  bandwidth percent 10
 class P11-DSCP-NETWORK-CONTROL
  bandwidth percent 5
 class P11-DSCP-BULK
  bandwidth percent 15
 class class-default
  fair-queue
!
policy-map P11-WAN-SHAPE-1M
 class class-default
  shape average 1000000
  service-policy P11-WAN-QUEUE
!
interface Ethernet0/0.100
 service-policy input P11-MARK-IN
!
interface Ethernet0/1
 service-policy output P11-WAN-SHAPE-1M
!
end
write memory
```

## Step 7 — Remaining Services (T+50 to T+60)

```ios
configure terminal
!
snmp-server community P09-RO-COMM ro
snmp-server host 10.1.99.11 traps version 2c P09-RO-COMM
!
logging host 10.1.99.11
logging trap informational
logging source-interface Loopback0
!
ip sla responder
!
ntp server 10.0.255.1 prefer
!
end
write memory
```

## Completion Target

HQ-RTR1 rebuild target: **T+60 minutes or less**

Proceed to HQ-DSW1 rebuild (Phase 3) immediately after.
