# Phase 2 — Inventory Validation

## Inventory

```text
project-13-network-automation/configs/inventory-devices.yml
```

## Validation Rules

- each device has `name`, `host`, `platform`, and `role`
- host IPs are unique
- device names are unique
- platform is supported by the collector
- no credential-like keys exist in inventory

## Expected Command

```bash
python scripts/collect_baseline.py --inventory configs/inventory-devices.yml --check-inventory-only
```

## Expected Result

```text
Inventory OK: 10 devices, 10 Netmiko-enabled
```
