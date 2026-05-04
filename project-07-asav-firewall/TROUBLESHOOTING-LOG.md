# Project 07 — Troubleshooting Log

Project-local troubleshooting entries for the ASAv perimeter firewall lab.

---

## Current Status

Phases 1-6 completed without a live unresolved issue requiring a repair entry. Verification evidence is captured under [verification/screenshots/](verification/screenshots/), and the phase command flow is documented directly in [README.md](README.md).

---

## Deferred Break/Fix — Not Completed

### P07-BF-01 — Inside interface security level set to 0

**Status:** Deferred for future video demonstration. This fault has not been injected, fixed, or marked complete.

**Planned symptom:** Inside campus clients lose inside-to-outside connectivity because the ASA treats the inside interface as untrusted.

**Planned diagnosis path:**
```
packet-tracer input inside tcp 10.1.100.10 12345 203.0.113.100 80
show nameif
show interface ip brief
show running-config interface GigabitEthernet0/0
```

**Expected root cause when demonstrated:** `GigabitEthernet0/0` has `security-level 0` instead of `security-level 100`.

**Expected fix when demonstrated:**
```
interface GigabitEthernet0/0
 security-level 100
end
write memory
```

**Documentation rule:** Add a new dated entry after the future video demonstration is recorded. Do not convert this deferred plan into a completed troubleshooting entry until the fault is actually demonstrated and fixed.
