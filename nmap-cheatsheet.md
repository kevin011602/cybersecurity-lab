# Nmap cheat sheet
A concise cheat sheet for Nmap used in penetration testing workflows.

<p align="center">
	<img src="https://nmap.org/images/nmap-logo-256x256.png" alt="Nmap Logo" width="120">
</p>

## Workflow

### Discover ports → Enumerate services → Deep analysis
This represents a typical penetration testing flow:
first identify exposed services, then gather details, and finally perform deeper system analysis.

## Discovery
Identify open ports on the target.
```
nmap -sS -p- <ip>
'''
-sS: SYN scan (fast, does not complete the TCP three-way handshake)
-p-: Scans all ports (1–65535)
'''
```

## Enumeration
Analyze discovered services.
```
nmap -sV -sC -p <porte> <ip>
'''
-sV: Detects service versions (e.g., Apache, OpenSSH)
-sC: Runs default NSE scripts for additional information gathering
-p <ports>: Limits scan to previously discovered open ports
'''
```

## Deep Analysis
Perform deeper system-level inspection.
```
nmap -sV -O -p <porte> <ip>
# -O: Attempts to detect the operating system via TCP/IP fingerprinting
```

## UDP Scan
Scan common UDP services.
```
nmap -sU --top-ports 20 <ip>
# Tip: use -Pn if host is blocking ICMP/ping (firewall or filtered networks)
```

---

## Advanced Options

### Aggressive scan
```
nmap -A <ip>
'''
Combines: -sV, -O, -sC, and traceroute
Provides comprehensive information in a single scan
Requires root privileges for full functionality
Noisy and easily detectable, not suitable for stealth scenarios
'''
```
### Timing Templates
- `-T0`  Paranoid   extremely slow scan with maximum delay between packets
- `-T1`  Sneaky     very slow scan
- `-T2`  Polite     reduced network impact
- `-T3`  Normal     default balanced speed
- `-T4`  Aggressive fast scan, commonly used in CTFs
- `-T5`  Insane     extremely fast, high risk of packet loss and detection