# Project 13 Final Automation Report

- Rendered UTC: 2026-06-19T06:02:11.607955+00:00
- Scope: CML enterprise network automation workstation, IOS/IOL fleet, and ASA exception tracking

## Executive Summary

I built a network automation workflow around the same enterprise CML lab used in Projects 01-12. The workflow starts with a structured inventory, proves reachability, collects read-only baselines, backs up redacted running configs, checks compliance, and provides a dry-run-first config push path.

## Phase Results

| Phase | Evidence | Result |
|-------|----------|--------|
| 3 read-only collection | 10 devices attempted | 8 successful, 2 failed |
| 4 redacted backups | 10 devices attempted | 8 successful, 2 failed |
| 5 compliance | 10 devices attempted | 0 compliant, 8 non-compliant, 2 failed |
| 6 gated config push | 10 devices planned | applied=False |

## Portfolio Takeaway

This project demonstrates the DevNet side of the lab: I can turn a manually built network into an inventory-driven automation target, collect evidence at scale, detect configuration drift, and gate changes so automation is controlled instead of reckless.
