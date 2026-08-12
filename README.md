# Cybersecurity Lab

Raccolta tecnica di appunti, script e laboratori pratici. Il repository nasce per documentare il mio percorso all'interno di un corso di formazione sulla sicurezza informatica.

## Struttura

| Cartella | Contenuto |
|----------|-----------|
| `01_network_fundamentals/` | ARP spoofing, MITM, ICMP, MAC change, packet analysis, Netdiscover, Nmap, Masscan |
| `02_offensive_python_basics/` | Reverse shell, P2P node, SYN scanner, script delivery |
| `03_cryptography/` | Caesar cipher, Blockchain, Hybrid RSA-AES, Ransomware, SSL/TLS mTLS |
| `04_evasion_techniques/` | Command obfuscation, Veil, Shellter, Go EarlyBird, Discover scripts |
| `05_command_and_control/` | Caldera, Covenant, PowerShell Empire |
| `06_recon_auditing/` | Maltego, Nessus, Shodan/FOFA |
| `07_identity_management/` | FreeIPA |
| `Exploitations/` | Heartbleed, DirtyCOW, SQLi, XSS, WPA2, Android, SET, pivoting, ecc. |

## Lab Setup

Ambiente virtualizzato su VMware Workstation:

* **Attacker:** Kali Linux
* **Target:** Metasploitable 2, Lubuntu, Windows 7/10, SEEDUbuntu, Debian 7.11, CentOS Stream 9
* **Infrastructure:** pfSense, Tenable Nessus

## Disclaimer

Tutto il materiale qui presente è pubblicato esclusivamente a scopo didattico. L'utilizzo di queste tecniche e degli script contro sistemi per cui non si ha un'autorizzazione esplicita è illegale e punibile a norma di legge.