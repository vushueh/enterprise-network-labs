# Project 11 — Limitations And Homelab Expansion Path

## L-01 — NBAR Does Not Classify Live Traffic On IOL

**What happened:** `match protocol http` and `match protocol dns` accepted as valid syntax, but counters stayed at zero during live traffic tests. ACL-based classification confirmed the traffic was present.

**Why it happens:** IOL's NBAR Protocol Description Library (PDL) is limited. The image accepts the commands but does not perform deep packet inspection on live traffic the same way IOS XE does on real hardware or CSR1000V.

**Homelab fix:** Use CSR1000V or Catalyst 8000V images in CML. Both support the full IOS XE NBAR PDL with live protocol classification. Alternatively, test on real Cisco hardware (ISR 4000 series or ASR 1000 series) where NBAR is fully implemented.

---

## L-02 — AutoQoS Not Supported On IOL-L2

**What happened:** `auto qos` command rejected with `% Invalid input detected` on BR-ASW1.

**Why it happens:** IOL-L2 is a basic layer-2 simulation image. AutoQoS is an IOS feature that generates a full MQC policy automatically — it requires the full IOS feature set that IOL-L2 does not implement.

**Homelab fix:** Use IOSvL2 or Catalyst 9000V images in CML if available. On real hardware, AutoQoS is available on Catalyst 2960, 3750, and 4500 switches. The manual MQC design from Project 11 covers the same concepts with more transparency and is the preferred approach for understanding what AutoQoS generates.

---

## L-03 — WAN Output DSCP Class Counters Did Not Increment During HTTP Testing

**What happened:** `P11-DSCP-BULK` (AF11) counter on Ethernet0/1 stayed at zero during Phase 5 HTTP tests.

**Why it happens:** HTTP traffic to 10.1.40.10 (nginx) routes via the firewall path (next-hop 10.0.0.14), not toward BR-RTR1 via Ethernet0/1. The WAN queue only sees traffic destined to the branch — not DMZ or internet traffic.

**Homelab fix:** To fully exercise the WAN output queue, set up a test HTTP server at a branch address (10.2.x.x or 10.0.255.2). Traffic to branch destinations routes via Ethernet0/1 and will hit the DSCP queuing classes. This is not a platform limitation — it is a routing topology consideration.

---

## L-04 — Voice VLAN 500 Not Verified With A Real IP Phone

**What happened:** `switchport voice vlan 500` was configured and verified with `show interfaces switchport` (Voice VLAN: 500 confirmed). No IP phone or soft-phone endpoint was present to confirm VLAN tagging behavior at the endpoint.

**Why it happens:** CML IOL endpoints do not support 802.1p VLAN tagging that an IP phone uses for its voice stream. The configuration is correct — the missing piece is an endpoint that sends tagged VLAN 500 frames.

**Homelab fix:** Add a Cisco IP Phone (7960/8800 series) to the physical lab connected to BR-ASW1. The phone will negotiate the voice VLAN via CDP and send its audio in tagged VLAN 500 frames while the connected PC uses untagged data VLAN 100. This validates the full voice VLAN behavior.

---

## L-05 — No DSCP Marking Verification End-To-End

**What happened:** DSCP marking was confirmed at the ingress policy counter level (`Packets marked: 54`). The actual DSCP value in the IP header was not captured with a packet capture to prove the bit was set in transit.

**Why it happens:** IOL does not support embedded packet capture (EPC) or `monitor capture` commands available on IOS XE.

**Homelab fix:** On CSR1000V or real hardware, use:

```ios
monitor capture CAP interface Ethernet0/0.100 both
monitor capture CAP access-list <acl>
monitor capture CAP start
monitor capture CAP export flash:cap.pcap
```

Open the pcap in Wireshark and filter on DSCP field. AF11 = 0x28, EF = 0xB8 in the ToS byte.
