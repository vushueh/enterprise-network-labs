# SNMP Break/Fix Pilot

The Project 13 reference calls for a deliberate automation fault: push the
wrong SNMP community to one device, detect it with compliance, then repair it.

## Recommended Pilot Device

Use `HQ-ASW2` as the pilot only after:

- the read-only collector succeeds;
- redacted backup exists for the device;
- compliance check correctly detects the current SNMP standard;
- the safe marker push has been applied and rolled back successfully.

## Fault Injection

Do not run this until the user explicitly approves a live break/fix.

```ios
configure terminal
no snmp-server community <STANDARD_SNMP_RO_COMMUNITY> RO ACL-SNMP-MANAGERS
snmp-server community P13_WRONG_COMMUNITY RO ACL-SNMP-MANAGERS
end
write memory
```

## Expected Symptom

- SNMP polling that expects the standard community fails for `HQ-ASW2`.
- `compliance_check.py` reports `SNMP read-only standard present=fail`.

## Diagnosis

```bash
cd ~/netauto
source .venv/bin/activate
python scripts/compliance_check.py \
  --inventory inventory/devices.yml \
  --device HQ-ASW2 \
  --output-dir outputs/phase8-snmp-breakfix-diagnosis
```

## Fix

```ios
configure terminal
no snmp-server community P13_WRONG_COMMUNITY RO ACL-SNMP-MANAGERS
snmp-server community <STANDARD_SNMP_RO_COMMUNITY> RO ACL-SNMP-MANAGERS
end
write memory
```

Re-run compliance and save the before/after reports.
