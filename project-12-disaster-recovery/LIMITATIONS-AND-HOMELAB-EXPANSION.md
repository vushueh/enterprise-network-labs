# Project 12 — Limitations And Homelab Expansion Path

## L-01 — HQ-FW1 Full Recovery Not Tested

**What happened:** HQ-FW1 received a partial fault (NAT and ACL config cleared) rather than a full `write erase` + `reload`. The ASAv full recovery procedure was not exercised.

**Why it matters:** A real disaster that takes down HQ-FW1 (corrupted startup config, hardware failure) requires rebuilding the ASAv from scratch — security levels, interface config, NAT, ACLs, inspection policies, and VPN config. This is a more complex and time-consuming rebuild than IOL devices.

**Homelab expansion:** Run a dedicated ASAv DR exercise. Erase the HQ-FW1 startup config, reload it, and rebuild from the Project 07 documentation. Time it separately. Key ASAv-specific differences: `nameif` before `ip address`, `security-level` required, `same-security-traffic permit inter-interface` for DMZ routing, and `access-group` applied globally not per-interface.

---

## L-02 — Config Archive Recovery Not Tested

**What happened:** Project 09 configured TFTP-based config archive on all IOS devices (`archive path tftp://10.1.99.11/archive/$h`). This archive was not used as the recovery source during the rebuild — configs were restored from memory and documentation.

**Why it matters:** In a real DR, the config archive is faster and more accurate than typing from memory. The TFTP archive should be the first recovery path, with documentation as the fallback.

**Homelab expansion:** Before the next DR exercise, verify:
```ios
show archive
archive tar /xtract tftp://10.1.99.11/archive/HQ-RTR1-current.cfg
```
Practice restoring from the archive server directly. Verify the archive is current (last backup timestamp should be within 24 hours of the DR exercise).

---

## L-03 — No Automated Verification

**What happened:** Post-recovery verification was performed manually — 8 separate checks run one by one from the CLI. Manual verification takes 8–10 minutes and is subject to human error (missing a check, misreading output).

**Homelab expansion:** Project 13 (Network Automation) provides the foundation. Build a Python/Netmiko script that:
1. SSH into each device
2. Runs the 8 verification commands
3. Parses the output
4. Produces a pass/fail report

```python
# Concept — Phase 4 automated verification
checks = {
    "HQ-RTR1": [
        ("show ip ospf neighbor", "FULL"),
        ("show crypto isakmp sa", "QM_IDLE"),
        ("show policy-map interface Ethernet0/0.100", "P11-MARK-IN"),
    ]
}
```

This reduces verification from 10 minutes to under 60 seconds.

---

## L-04 — Single Engineer Rebuild

**What happened:** The rebuild was performed by a single engineer working sequentially. In a real enterprise DR with multiple engineers, HQ-RTR1 and HQ-DSW1 could be rebuilt in parallel — reducing total time significantly.

**Homelab expansion:** Practice a parallel rebuild with two CML console windows open simultaneously. One engineer rebuilds HQ-RTR1 while another rebuilds HQ-DSW1 from T+00:00. With parallel work, the 87-minute rebuild should complete in under 50 minutes since the HQ-DSW1 rebuild (20 minutes) overlaps with the second half of the HQ-RTR1 rebuild.

---

## L-05 — Branch And WAN-RTR1 Not Included In DR Scope

**What happened:** Only HQ-RTR1 and HQ-DSW1 were included in the disaster. BR-RTR1, WAN-RTR1, and all branch devices remained operational throughout.

**Homelab expansion:** Run a full-network DR scenario where ALL routers lose startup config simultaneously. This tests whether the engineer can restore OSPF across a completely blank network — the order becomes critical (can't test OSPF until at least two routers have IPs configured on shared links). This also tests the GRE/IPsec rebuild on both ends simultaneously.
