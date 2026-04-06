# Project 02 — Requirements

## Business Requirements
1. Connect a second site (Branch) to the existing HQ campus
2. Branch must have the same VLAN segmentation as HQ (Engineering, Sales, Guest, Voice, Management)
3. All endpoints at both sites must receive IP addresses automatically (DHCP)
4. A single centralized DHCP server must serve all VLANs at both sites
5. DNS must resolve infrastructure hostnames from any endpoint at either site
6. IPv6 must be operational on at least one VLAN at both sites
7. Management access via SSH must work from HQ to all branch devices

## Technical Requirements
- Branch switching: 1 distribution switch, 1 access switch
- WAN: point-to-point /30 between HQ-RTR1 and BR-RTR1
- Routing: static routes for all subnets in both directions
- DHCP server: Linux-based Dnsmasq on HQ management VLAN (10.1.99.50)
- DHCP relay: ip helper-address on all router subinterfaces at both sites
- IPv6: dual-stack on WAN and VLAN 100 at both sites, SLAAC for endpoints
- DNS: static A records for all infrastructure devices, resolvable from endpoints and routers
- Security baseline: SSH v2, exec-timeout 10 0, service password-encryption, logging buffered 8192

## Success Criteria
- [ ] PC-BR1 and PC-BR2 receive DHCP addresses from 10.1.99.50
- [ ] HQ endpoints receive DHCP addresses from 10.1.99.50
- [ ] Cross-site ping: HQ-RTR1 can reach 10.2.99.3 (BR-ASW1 management)
- [ ] IPv6 cross-site: HQ-RTR1 can ping 2001:db8:2:100::1
- [ ] PC-BR1 SLAAC address appears in 2001:db8:2:100::/64
- [ ] nslookup hq-rtr1.lab.local returns 10.1.99.1 from PC-BR1
- [ ] BR-RTR1 can ping hq-rtr1.lab.local by name
- [ ] SSH from PC-MGMT1 to BR-DSW1 succeeds
